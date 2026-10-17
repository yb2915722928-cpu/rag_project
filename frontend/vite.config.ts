import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      // Generated public contracts live outside the frontend root; alias keeps
      // imports type-checked and bundled without copying the generated files.
      '@contracts': fileURLToPath(new URL('../contracts/typescript', import.meta.url)),
    },
  },
})
