import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  root: path.resolve(__dirname),
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000'
    }
  }
})
