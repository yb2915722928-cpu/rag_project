import { describe, expect, it } from 'vitest'

import type { JobState, PublicError, RetryMode } from '@contracts/contracts'
import type { OperationResponse as OperationInput } from '@contracts/contracts.input'

describe('generated contract types', () => {
  it('resolves the @contracts alias and keeps enum unions usable', () => {
    const error: PublicError = {
      code: 'INTERNAL_ERROR',
      message: 'kept server-side; frontend tests only exercise the type surface',
      http_status: 500,
      retry_mode: 'none' satisfies RetryMode,
    }
    const state: JobState = 'queued'
    expect(error.http_status).toBe(500)
    expect(state).toBe('queued')
  })

  it('input-side models stay distinct from serialization models', () => {
    const payload: Partial<OperationInput> = { schema_version: 'operation.v1' }
    expect(payload.schema_version).toBe('operation.v1')
  })
})
