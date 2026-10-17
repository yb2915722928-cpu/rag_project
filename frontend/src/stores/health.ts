import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import type { PublicError } from '@contracts/contracts'

import { fetchHealth, FetchTimeoutError, type HealthStatusBody } from '@/api/health'

export type HealthPhase =
  | 'idle'
  | 'loading'
  | 'success'
  | 'http-error'
  | 'invalid-body'
  | 'timeout'
  | 'network-error'

export const HEALTH_TIMEOUT_MS = 5000

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

/** The health body is an OpenAPI object with free-form string fields; only
 *  validate the wire shape, never treat it as a database/business signal. */
function parseHealthBody(value: unknown): HealthStatusBody | null {
  if (!isRecord(value)) {
    return null
  }
  const out: HealthStatusBody = {}
  for (const key of ['status', 'service', 'check'] as const) {
    const field = value[key]
    if (field === undefined) {
      continue
    }
    if (typeof field !== 'string') {
      return null
    }
    out[key] = field
  }
  return out
}

/** Error responses follow the public PublicError policy; extract the stable
 *  code only, never the raw message/details (may carry private text). */
function extractErrorCode(value: unknown): PublicError['code'] | undefined {
  if (!isRecord(value)) {
    return undefined
  }
  const code = value.code
  return typeof code === 'string' ? (code as PublicError['code']) : undefined
}

export const useHealthStore = defineStore('health', () => {
  const phase = ref<HealthPhase>('idle')
  const httpStatus = ref<number | undefined>(undefined)
  const body = ref<HealthStatusBody | null>(null)
  const errorCode = ref<PublicError['code'] | undefined>(undefined)
  const lastUpdatedAt = ref<number | null>(null)
  const checkedAt = ref<number | null>(null)

  const phaseSequence = ref(0)
  let controller: AbortController | null = null

  const loading = computed(() => phase.value === 'loading')

  function setPhase(next: HealthPhase): number {
    phaseSequence.value += 1
    phase.value = next
    return phaseSequence.value
  }

  function resetResult(): void {
    httpStatus.value = undefined
    body.value = null
    errorCode.value = undefined
  }

  /** Single-flight refresh: a new request aborts the previous one and every
   *  in-flight resolution is fenced by the phase sequence, so there is never
   *  automatic retry or a stale late write. */
  async function refresh(): Promise<void> {
    controller?.abort()
    const next = new AbortController()
    controller = next
    const seq = setPhase('loading')
    resetResult()

    try {
      const result = await fetchHealth({
        signal: next.signal,
        timeoutMs: HEALTH_TIMEOUT_MS,
      })
      if (seq !== phaseSequence.value) {
        return
      }
      httpStatus.value = result.status
      checkedAt.value = Date.now()

      if (!result.ok) {
        const parsed = result.json
        errorCode.value = parsed === undefined ? undefined : extractErrorCode(parsed)
        phase.value = 'http-error'
        return
      }

      const parsed = parseHealthBody(result.json)
      if (parsed === null) {
        phase.value = 'invalid-body'
        return
      }
      body.value = parsed
      errorCode.value = undefined
      phase.value = 'success'
      lastUpdatedAt.value = checkedAt.value
    } catch (error) {
      if (seq !== phaseSequence.value || next.signal.aborted) {
        return
      }
      checkedAt.value = Date.now()
      if (error instanceof FetchTimeoutError) {
        phase.value = 'timeout'
        return
      }
      phase.value = 'network-error'
    } finally {
      if (seq === phaseSequence.value && controller === next) {
        controller = null
      }
    }
  }

  function reset(): void {
    controller?.abort()
    controller = null
    setPhase('idle')
    resetResult()
    lastUpdatedAt.value = null
    checkedAt.value = null
  }

  return {
    phase,
    loading,
    httpStatus,
    body,
    errorCode,
    lastUpdatedAt,
    checkedAt,
    refresh,
    reset,
  }
})
