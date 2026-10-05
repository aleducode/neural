import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Nombres fijos y sin hash: de eso se encarga WhiteNoise en collectstatic, y
// asi las plantillas pueden referenciarlos con {% static %}.
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": path.resolve(__dirname, "src") } },
  build: {
    outDir: path.resolve(__dirname, "../neural/manager/static/manager/bundle"),
    emptyOutDir: true,
    manifest: false,
    rollupOptions: {
      input: path.resolve(__dirname, "src/main.tsx"),
      output: {
        entryFileNames: "manager.js",
        assetFileNames: "manager.[ext]",
      },
    },
  },
});
