import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 1420,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8765',
        changeOrigin: true,
        headers: { 'x-forge-token': 'af-local-ipc-token-2026' },
      },
    },
  },
  build: { outDir: 'dist', emptyOutDir: true },
});
