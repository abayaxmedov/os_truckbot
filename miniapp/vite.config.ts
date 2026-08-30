import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

// Telegram Mini Apps must be served over HTTPS in production; in local dev we
// proxy /api and /media to the backend so everything is same-origin.
const BACKEND = process.env.VITE_BACKEND_URL || "http://localhost:8010";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
  server: {
    port: 5173,
    host: true,
    // Allow serving over an HTTPS dev tunnel (cloudflared/ngrok) for Telegram testing.
    allowedHosts: true,
    proxy: {
      "/api": { target: BACKEND, changeOrigin: true },
      "/media": { target: BACKEND, changeOrigin: true },
    },
  },
});
