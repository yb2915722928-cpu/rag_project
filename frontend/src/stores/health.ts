import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import type { FailedResponse, PublicError } from '@contracts/contracts'

import { fetchHealth, FetchTimeoutError } from '@/api/health'

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

/** A reachable 2xx only means "the API answered" (reachability); the payload
 *  shape is not consumed as a database/business signal. */
function isReachableBody(value: unknown): boolean {
  return isRecord(value)
}

/** FailedResponse envelope: the public error lives at body.error (see
 *  contracts/typescript/contracts.ts). Extract the stable code only, never
 *  the raw message/details (may carry private text). */
function extractErrorCode(value: unknown): PublicError['code'] | undefined {
  if (!isRecord(value)) {
    return undefined
  }
  const error = (value as Partial<FailedResponse>).error
  if (!isRecord(error)) {
    return undefined
  }
  const code = error.code
  return typeof code === 'string' ? (code as PublicError['code']) : undefined
}

export const useHealthStore = defineStore('health', () => {
  const phase = ref<HealthPhase>('idle')
  const httpStatus = ref<number | undefined>(undefined)
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

      if (!isReachableBody(result.json)) {
        phase.value = 'invalid-body'
        return
      }
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
    errorCode,
    lastUpdatedAt,
    checkedAt,
    refresh,
    reset,
  }
})
