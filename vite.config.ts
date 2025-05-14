import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory
  const env = loadEnv(mode, process.cwd())
  
  return {
    plugins: [vue()],
    define: {
      'process.env': env,
      'import.meta.env.VUE_APP_API_URL': JSON.stringify(env.VUE_APP_API_URL || 'http://127.0.0.1:8000'),
    },
  }
})
