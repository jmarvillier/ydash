import { fileURLToPath, URL } from 'node:url';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';
import { readBuildInfo, versionPlugin } from './build/versionPlugin';

// `VITE_BASE` : `/ydash/` (prod), `/ydash/staging/` (staging), `/` en local.
const base = process.env.VITE_BASE ?? '/';
const buildInfo = readBuildInfo(fileURLToPath(new URL('./package.json', import.meta.url)));

export default defineConfig({
  base,
  plugins: [
    react(),
    versionPlugin(buildInfo, fileURLToPath(new URL('./build/sw.template.js', import.meta.url))),
  ],
  resolve: {
    alias: {
      '@core': fileURLToPath(new URL('../core/src', import.meta.url)),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
  },
});
