export interface HealthFetchResult {
  ok: boolean
  status: number
  /** Present only when the response parses as a JSON object; never exposed
   *  raw to the UI. */
  json?: Record<string, unknown>
}

export class FetchTimeoutError extends Error {
  constructor(timeoutMs: number) {
    super(`request timed out after ${timeoutMs}ms`)
    this.name = 'FetchTimeoutError'
  }
}

export interface FetchHealthOptions {
  signal?: AbortSignal
  timeoutMs?: number
}

/** Same-origin GET /health (liveness only). A reachable 2xx means the API
 *  answered; it does not attest database readiness or business success. */
export async function fetchHealth(options: FetchHealthOptions = {}): Promise<HealthFetchResult> {
  const { signal, timeoutMs = 5000 } = options
  if (signal?.aborted) {
    throw new DOMException('The operation was aborted.', 'AbortError')
  }

  const controller = new AbortController()
  const onAbort = (): void => controller.abort()
  signal?.addEventListener('abort', onAbort, { once: true })
  const timer = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetch('/health', {
      method: 'GET',
      headers: { Accept: 'application/json' },
      cache: 'no-store',
      signal: controller.signal,
    })

    let json: Record<string, unknown> | undefined
    try {
      const parsed: unknown = await response.json()
      if (typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed)) {
        json = parsed as Record<string, unknown>
      }
    } catch {
      json = undefined
    }

    return { ok: response.ok, status: response.status, json }
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      if (signal?.aborted) {
        throw error
      }
      throw new FetchTimeoutError(timeoutMs)
    }
    throw error
  } finally {
    clearTimeout(timer)
    signal?.removeEventListener('abort', onAbort)
  }
}
