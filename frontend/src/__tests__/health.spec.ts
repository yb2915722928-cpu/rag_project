import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { FetchTimeoutError, fetchHealth } from '@/api/health'
import { useHealthStore } from '@/stores/health'

interface MockResponseInit {
  status?: number
  body?: unknown
  rawBody?: string
}

function mockFetchOnce(init: MockResponseInit): void {
  const payload = init.rawBody ?? JSON.stringify(init.body ?? {})
  const response = new Response(payload, {
    status: init.status ?? 200,
    headers: { 'Content-Type': 'application/json' },
  })
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response))
}

function fetchMock(): ReturnType<typeof vi.fn> {
  return fetch as unknown as ReturnType<typeof vi.fn>
}

describe('fetchHealth', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.useRealTimers()
  })

  it('requests same-origin /health without retries', async () => {
    mockFetchOnce({ body: { status: 'alive', service: 'rag-api', check: 'liveness' } })
    const result = await fetchHealth()
    expect(result.ok).toBe(true)
    expect(result.status).toBe(200)
    expect(fetchMock()).toHaveBeenCalledTimes(1)
    const [url, options] = fetchMock().mock.calls[0] as [string, RequestInit]
    expect(url).toBe('/health')
    expect(options.method).toBe('GET')
  })

  it('reports non-2xx as not ok with parsed json for code extraction', async () => {
    mockFetchOnce({
      status: 503,
      body: {
        status: 'failed',
        request_id: 'req-1',
        schema_version: 'operation.v1',
        error: {
          code: 'DEPENDENCY_UNAVAILABLE',
          message: 'private detail',
          http_status: 503,
          retry_mode: 'none',
        },
      },
    })
    const result = await fetchHealth()
    expect(result.ok).toBe(false)
    expect(result.status).toBe(503)
    expect((result.json?.error as Record<string, unknown> | undefined)?.code).toBe(
      'DEPENDENCY_UNAVAILABLE',
    )
  })

  it('distinguishes timeout from caller abort', async () => {
    vi.useFakeTimers()
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((_url: string, init: RequestInit) => {
        return new Promise((_resolve, reject) => {
          init.signal?.addEventListener('abort', () => {
            reject(new DOMException('The operation was aborted.', 'AbortError'))
          })
        })
      }),
    )
    const pending = fetchHealth({ timeoutMs: 1000 })
    const assertion = expect(pending).rejects.toBeInstanceOf(FetchTimeoutError)
    await vi.advanceTimersByTimeAsync(1000)
    await assertion
  })

  it('propagates caller abort as AbortError', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((_url: string, init: RequestInit) => {
        return new Promise((_resolve, reject) => {
          init.signal?.addEventListener('abort', () => {
            reject(new DOMException('The operation was aborted.', 'AbortError'))
          })
        })
      }),
    )
    const controller = new AbortController()
    const pending = fetchHealth({ signal: controller.signal, timeoutMs: 60000 })
    controller.abort()
    await expect(pending).rejects.toMatchObject({ name: 'AbortError' })
  })
})

describe('health store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('starts idle and records reachability success without consuming payload fields', async () => {
    mockFetchOnce({ body: { status: 'alive', service: 'rag-api', check: 'liveness' } })
    const store = useHealthStore()
    expect(store.phase).toBe('idle')
    await store.refresh()
    expect(store.phase).toBe('success')
    expect(store.httpStatus).toBe(200)
    expect(store.errorCode).toBeUndefined()
    expect(fetchMock()).toHaveBeenCalledTimes(1)
  })

  it('accepts an empty object body (only object-ness is required)', async () => {
    mockFetchOnce({ body: {} })
    const store = useHealthStore()
    await store.refresh()
    expect(store.phase).toBe('success')
  })

  it('reads error code from the FailedResponse envelope, never the raw message', async () => {
    mockFetchOnce({
      status: 500,
      body: {
        status: 'failed',
        request_id: 'req-2',
        schema_version: 'operation.v1',
        error: {
          code: 'INTERNAL_ERROR',
          message: 'private database url: postgres://internal-host/db',
          http_status: 500,
          retry_mode: 'none',
          details: { trace_id: 'abc' },
        },
      },
    })
    const store = useHealthStore()
    await store.refresh()
    expect(store.phase).toBe('http-error')
    expect(store.httpStatus).toBe(500)
    expect(store.errorCode).toBe('INTERNAL_ERROR')
    const snapshot = JSON.stringify(store.$state)
    expect(snapshot).not.toContain('postgres://')
    expect(snapshot).not.toContain('internal-host')
    expect(snapshot).not.toContain('trace_id')
  })

  it('flags non-object bodies as invalid', async () => {
    mockFetchOnce({ rawBody: '"just-a-string"' })
    const store = useHealthStore()
    await store.refresh()
    expect(store.phase).toBe('invalid-body')
  })

  it('maps timeout to the timeout phase', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new FetchTimeoutError(5000)))
    const store = useHealthStore()
    await store.refresh()
    expect(store.phase).toBe('timeout')
  })

  it('maps connection failures to the network-error phase', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    const store = useHealthStore()
    await store.refresh()
    expect(store.phase).toBe('network-error')
  })

  it('keeps the latest request authoritative when a refresh supersedes an earlier one', async () => {
    let resolveFirst: ((r: Response) => void) | undefined
    let resolveSecond: ((r: Response) => void) | undefined
    const responses = [
      new Promise<Response>((resolve) => {
        resolveFirst = resolve
      }),
      new Promise<Response>((resolve) => {
        resolveSecond = resolve
      }),
    ]
    const impl = vi.fn()
    impl.mockImplementationOnce(() => responses[0])
    impl.mockImplementationOnce(() => responses[1])
    vi.stubGlobal('fetch', impl)

    const store = useHealthStore()
    const first = store.refresh()
    const second = store.refresh()

    resolveSecond?.(
      new Response(JSON.stringify({ status: 'alive' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    resolveFirst?.(
      new Response(JSON.stringify({ status: 'stale' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    await Promise.all([first, second])

    expect(store.phase).toBe('success')
    expect(impl).toHaveBeenCalledTimes(2)
  })

  it('does not leave loading state when the caller aborts', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((_url: string, init: RequestInit) => {
        return new Promise((_resolve, reject) => {
          init.signal?.addEventListener('abort', () => {
            reject(new DOMException('The operation was aborted.', 'AbortError'))
          })
        })
      }),
    )
    const store = useHealthStore()
    const pending = store.refresh()
    store.reset()
    await pending
    expect(store.phase).toBe('idle')
  })
})
