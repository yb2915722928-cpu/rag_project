# MaxKB source excerpt: ui/vite.config.ts

- source: https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/ui/vite.config.ts
- raw: https://raw.githubusercontent.com/1Panel-dev/MaxKB/0fa9a0dae8850c1878f087f0d81c974c1d424b06/ui/vite.config.ts
- publisher: 1Panel-dev/MaxKB
- pub_date: 未标
- accessed: 2026-10-15
- confidence: medium（单一官方源）
- class: official-pinned-source

```text
63:   proxyConf[`^${ENV.VITE_BASE_PATH}.+\/oss\/file\/.*$`] = {
64:     target: `http://127.0.0.1:8080`,
65:     changeOrigin: true,
66:   }
67:   // 前端静态资源转发到本身
68:   proxyConf[`^${ENV.VITE_BASE_PATH}oss\/file\/.*$`] = {
69:     target: `http://127.0.0.1:8080`,
70:     changeOrigin: true,
71:   }
72:   proxyConf[`^${ENV.VITE_BASE_PATH}oss\/get_url\/.*$`] = {
73:     target: `http://127.0.0.1:8080`,
74:     changeOrigin: true,
75:   }
...
83:   return {
84:     preflight: false,
85:     lintOnSave: false,
86:     base: './',
87:     envDir: envDir,
88:     plugins: [
89:       vue(),
90:       vueJsx(),
91:       DefineOptions(),
92:       createHtmlPlugin({template: ENV.VITE_ENTRY}),
93:       renameHtmlPlugin(`dist${ENV.VITE_BASE_PATH}`, ENV.VITE_ENTRY),
94:     ],
95:     server: {
96:       cors: true,
97:       host: '0.0.0.0',
98:       port: Number(ENV.VITE_APP_PORT),
99:       strictPort: true,
100:       proxy: proxyConf,
101:     },
102:     build: {
103:       outDir: `dist${ENV.VITE_BASE_PATH}`,
104:       target: 'es2022',
105:       rollupOptions: {
106:         input: ENV.VITE_ENTRY,
107:       },
108:     },
```
