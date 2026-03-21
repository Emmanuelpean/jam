import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";

export default defineConfig({
	plugins: [react(), svgr()],
	base: "/jam",
	server: {
		port: 3000,
	},
	test: {
		environment: "jsdom",
		globals: true,
	},
});
