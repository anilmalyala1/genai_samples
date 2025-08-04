import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Proxy API requests during development to the FastAPI backend.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/query': 'http://localhost:8000',
    },
  },
});

