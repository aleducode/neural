import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

/** Solo para el preview local de dev/. El build de produccion usa vite.config.ts. */
export default defineConfig({
  plugins: [react()],
  root: path.resolve(__dirname, "dev"),
  resolve: { alias: { "@": path.resolve(__dirname, "src") } },
  server: { port: 5174, open: true },
});
