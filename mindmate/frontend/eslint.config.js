import js from "@eslint/js";
import tseslint from "typescript-eslint";
import globals from "globals";

export default tseslint.config(
  { ignores: ["dist", "node_modules", "coverage"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      globals: { ...globals.browser },
    },
  },
  {
    // Test + node files get node globals.
    files: ["**/*.test.{ts,tsx}", "**/mocks/**", "vite.config.ts"],
    languageOptions: { globals: { ...globals.node } },
  },
);