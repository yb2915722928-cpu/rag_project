<script setup lang="ts">
import { computed, onMounted } from 'vue'

import { useHealthStore, HEALTH_TIMEOUT_MS } from '@/stores/health'

const store = useHealthStore()

const RETRY_HINT = '可稍后使用“重新检查”重试；若持续失败请联系管理员并提供最近检查时间。'

interface ErrorCopy {
  title: string
  description: string
}

const errorCopy = computed<ErrorCopy | null>(() => {
  switch (store.phase) {
    case 'http-error': {
      const parts = [`健康检查接口返回 HTTP ${store.httpStatus ?? '未知状态'}。`]
      if (store.errorCode !== undefined) {
        parts.push(`错误代码：${store.errorCode}。`)
      }
      parts.push('接口可达但当前不可用；这不代表业务数据正常。', RETRY_HINT)
      return { title: '健康检查接口返回错误', description: parts.join(' ') }
    }
    case 'invalid-body':
      return {
        title: '响应格式不符合约定',
        description: `健康检查响应不是预期的 JSON 对象结构。${RETRY_HINT}`,
      }
    case 'timeout':
      return {
        title: '请求超时',
        description: `超过 ${HEALTH_TIMEOUT_MS / 1000} 秒未收到健康检查响应。${RETRY_HINT}`,
      }
    case 'network-error':
      return {
        title: '网络错误',
        description: `未能连接到健康检查接口。${RETRY_HINT}`,
      }
    default:
      return null
  }
})

const statusText = computed(() => {
  switch (store.phase) {
    case 'idle':
      return '尚未检查'
    case 'loading':
      return '检查中…'
    case 'success':
      return '接口可达'
    case 'http-error':
      return '接口返回错误'
    case 'invalid-body':
      return '响应格式异常'
    case 'timeout':
      return '请求超时'
    case 'network-error':
      return '网络错误'
    default:
      return '未知'
  }
})

const tagType = computed<'info' | 'success' | 'danger' | 'warning'>(() => {
  switch (store.phase) {
    case 'success':
      return 'success'
    case 'http-error':
    case 'timeout':
    case 'network-error':
      return 'danger'
    case 'invalid-body':
      return 'warning'
    default:
      return 'info'
  }
})

const showResult = computed(() => store.phase !== 'idle' && store.phase !== 'loading')

function formatTime(timestamp: number | null): string {
  if (timestamp === null) {
    return '—'
  }
  return new Intl.DateTimeFormat('zh-CN', {
    dateStyle: 'short',
    timeStyle: 'medium',
    hour12: false,
  }).format(new Date(timestamp))
}

function refresh(): void {
  void store.refresh()
}

onMounted(() => {
  void store.refresh()
})
</script>

<template>
  <div class="page">
    <main class="panel" aria-labelledby="page-title">
      <h1 id="page-title" class="page-title">健康状态</h1>

      <p class="note">
        本页面仅确认前端已加载、同源 <code>/health</code> 接口可达。接口可达不代表数据库已就绪，也不代表业务功能正常。
      </p>

      <div class="status-line">
        <el-tag :type="tagType" disable-transitions>{{ statusText }}</el-tag>
        <el-button type="primary" :loading="store.loading" @click="refresh">
          {{ store.loading ? '检查中' : '重新检查' }}
        </el-button>
      </div>

      <div v-if="store.loading" v-loading="true" class="loading-region" aria-label="正在检查" />

      <section
        v-if="showResult && store.phase === 'success'"
        class="result"
        aria-label="健康检查结果"
      >
        <dl>
          <div class="row">
            <dt>HTTP 状态</dt>
            <dd>{{ store.httpStatus }}</dd>
          </div>
          <div class="row">
            <dt>最近检查时间</dt>
            <dd>{{ formatTime(store.lastUpdatedAt) }}</dd>
          </div>
        </dl>
      </section>

      <el-alert
        v-if="errorCopy !== null"
        class="error-alert"
        type="error"
        :title="errorCopy.title"
        :description="errorCopy.description"
        show-icon
        :closable="false"
        role="alert"
      />
    </main>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-5) var(--space-4);
}

.panel {
  width: 100%;
  max-width: 720px;
  margin-top: var(--space-6);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--panel-padding);
}

.page-title {
  margin: 0 0 var(--space-3);
  font-size: 20px;
  font-weight: 600;
  line-height: 1.4;
}

.note {
  margin: 0 0 var(--space-5);
  color: var(--color-text-secondary);
}

.note code {
  font-family: var(--font-code);
  font-size: 13px;
}

.status-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2) var(--space-3);
  margin-bottom: var(--space-5);
}

.status-line .el-tag {
  min-height: var(--touch-target);
  padding: 0 var(--space-3);
  display: inline-flex;
  align-items: center;
  font-size: 14px;
}

.loading-region {
  min-height: 96px;
}

.result dl {
  margin: 0;
}

.row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-3);
  padding: var(--space-3) 0;
  border-top: 1px solid var(--color-border);
}

.row dt {
  min-width: 160px;
  color: var(--color-text-secondary);
}

.row dd {
  margin: 0;
  color: var(--color-text-primary);
  overflow-wrap: anywhere;
}

.error-alert {
  margin-top: var(--space-4);
}

@media (max-width: 767px) {
  .page {
    padding: var(--space-4);
  }

  .panel {
    margin-top: var(--space-4);
    padding: var(--space-4);
  }
}
</style>
