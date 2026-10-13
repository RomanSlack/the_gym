import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const rev = (() => {
  try { return execSync("git rev-parse --short HEAD").toString().trim(); } catch { return "uncommitted"; }
})();

// the layout page (layout.html) reads + saves model/layouts/*.json through this tiny dev endpoint
const layoutApi = {
  name: "layout-api",
  configureServer(server: any) {
    server.middlewares.use("/api/layout", (req: any, res: any) => {
      const f = path.resolve(__dirname, "../model/layouts", (new URL(req.url, "http://x").searchParams.get("name") || "lockers").replace(/[^a-z0-9_-]/gi, "") + ".json");
      if (req.method === "POST") {
        let body = "";
        req.on("data", (c: Buffer) => (body += c));
        req.on("end", () => { JSON.parse(body); fs.writeFileSync(f, body); res.end("saved"); });
        return;
      }
      res.setHeader("Content-Type", "application/json"); res.end(fs.readFileSync(f));
    });
  },
};

export default defineConfig({
  plugins: [react(), layoutApi],
  build: { rollupOptions: { input: { main: path.resolve(__dirname, "index.html"), layout: path.resolve(__dirname, "layout.html") } } },
  define: { __REV__: JSON.stringify(rev) },
  // the model and reference data live outside this folder, at the repo root
  server: { fs: { allow: [".."] }, port: 5280 },
});
