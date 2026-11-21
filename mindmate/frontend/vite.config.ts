import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// defineConfig from vitest/config extends Vite's config with the `test` field.
// Tailwind v4 is wired through its Vite plugin (no tailwind.config.js / PostCSS).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
  },
});