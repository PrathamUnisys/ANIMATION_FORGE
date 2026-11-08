import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const token = env.ANIMATION_FORGE_IPC_TOKEN;
  return {
    plugins: [react()],
    server: {
      host: '127.0.0.1',
      port: 1420,
      strictPort: true,
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8765',
          changeOrigin: true,
          headers: token ? { 'x-forge-token': token } : {},
        },
      },
    },
    build: { outDir: 'dist', emptyOutDir: true },
  };
});
