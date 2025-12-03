import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(() => ({
  server: {
    host: "::",
    port: 5173,
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  define: {
    // Disable any development overlays or watermarks
    __DEV__: false,
    'process.env.NODE_ENV': '"production"',
  },
  build: {
    // Remove any development artifacts
    minify: true,
    sourcemap: false,
  },
}));
