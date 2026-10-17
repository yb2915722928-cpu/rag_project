import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import HealthView from '@/views/HealthView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'health',
    component: HealthView,
    meta: { title: '健康状态' },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
