import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { execSync } from "node:child_process";

const rev = (() => {
  try { return execSync("git rev-parse --short HEAD").toString().trim(); } catch { return "uncommitted"; }
})();

export default defineConfig({
  plugins: [react()],
  define: { __REV__: JSON.stringify(rev) },
  // the model and reference data live outside this folder, at the repo root
  server: { fs: { allow: [".."] }, port: 5280 },
});
