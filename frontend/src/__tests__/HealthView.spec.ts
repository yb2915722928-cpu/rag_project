import { afterEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'

import HealthView from '@/views/HealthView.vue'

function mockFetch(status: number, body: unknown): ReturnType<typeof vi.fn> {
  const impl = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(body), {
      status,
      headers: { 'Content-Type': 'application/json' },
    }),
  )
  vi.stubGlobal('fetch', impl)
  return impl
}

function mountView() {
  return mount(HealthView, {
    global: {
      plugins: [createPinia(), ElementPlus],
    },
    attachTo: document.body,
  })
}

describe('HealthView', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    document.body.innerHTML = ''
  })

  it('renders the reachability notice and does not claim db readiness', async () => {
    mockFetch(200, { status: 'alive', service: 'rag-api', check: 'liveness' })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('接口可达')
    })
    const text = wrapper.text()
    expect(text).toContain('不代表数据库已就绪')
    expect(text).toContain('alive')
    wrapper.unmount()
  })

  it('shows a readable error without raw body on HTTP failure', async () => {
    mockFetch(500, {
      code: 'INTERNAL_ERROR',
      message: 'postgres://secret-internal-url',
      http_status: 500,
      retry_mode: 'none',
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('接口返回错误')
    })
    const text = wrapper.text()
    expect(text).toContain('HTTP 500')
    expect(text).toContain('INTERNAL_ERROR')
    expect(text).not.toContain('postgres://')
    wrapper.unmount()
  })

  it('manual refresh triggers a new single request', async () => {
    const impl = mockFetch(200, { status: 'alive' })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('接口可达')
    })
    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeUndefined()
    await button.trigger('click')
    await vi.waitFor(() => {
      expect(impl.mock.calls.length).toBe(2)
    })
    wrapper.unmount()
  })
})
