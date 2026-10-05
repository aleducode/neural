import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Nombres fijos y sin hash: de eso se encarga WhiteNoise en collectstatic, y
// asi las plantillas pueden referenciarlos con {% static %}.
export default defineConfig({
  // Las url() de la CSS --las de Geist-- se resuelven contra esta base, que es
  // donde Django sirve el bundle.
  base: "/static/manager/bundle/",
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
        // La hoja va con nombre fijo porque la plantilla la nombra; los
        // demas assets (las fuentes) llevan hash o se pisarian entre si.
        assetFileNames: (info) =>
          info.names?.some((name) => name.endsWith(".css"))
            ? "manager.css"
            : "assets/[name]-[hash][extname]",
      },
    },
  },
});
