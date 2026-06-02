import { defineConfig } from "vite";
import { fileURLToPath } from "node:url";

const page = (path) => fileURLToPath(new URL(path, import.meta.url));

export default defineConfig({
  base: "/lanicaonewsletters/",
  build: {
    rollupOptions: {
      input: {
        main: page("index.html"),
        may2026: page("may-2026.html"),
      },
    },
  },
});
