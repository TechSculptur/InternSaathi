import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.svg", "icon-192.png", "icon-512.png"],
      manifest: {
        name: "Internship Saathi",
        short_name: "Saathi",
        description: "Accessible prototype internship recommender inspired by the PM Internship Scheme",
        theme_color: "#059669",
        background_color: "#f8fafc",
        display: "standalone",
        start_url: "/",
        icons: [
          {
            src: "/icon-192.png",
            sizes: "192x192",
            type: "image/png",
          },
          {
            src: "/icon-512.png",
            sizes: "512x512",
            type: "image/png",
          },
        ],
      },
      workbox: {
        // Only cache local static assets and HTML shell; NEVER cache API responses or recommendation requests
        globPatterns: ["**/*.{js,css,html,ico,png,svg}"],
        navigateFallback: "/index.html",
        navigateFallbackDenylist: [/^\/api/],
      },
    }),
  ],
  server: {
    port: 5173,
    host: "127.0.0.1",
    proxy: {
      "/api/v1": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/tests/setup.ts",
  },
});
