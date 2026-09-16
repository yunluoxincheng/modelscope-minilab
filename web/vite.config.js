import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// 本地开发：npm run dev 后 /api 由 Vite 代理到本机后端（uvicorn 默认 8000 端口）。
// 生产环境：默认走同源 /api（nginx 容器内反代到 backend 服务），无需构建期注入地址。
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus', '@element-plus/icons-vue'],
          vendor: ['vue', 'vue-router', 'axios'],
        },
      },
    },
  },
});
