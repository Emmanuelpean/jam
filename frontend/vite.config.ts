import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";
import checker from "vite-plugin-checker";

export default defineConfig({
	plugins: [react(), svgr(), checker({ typescript: true })],
	base: "/jam",
	server: {
		port: 3000,
	},
	test: {
		environment: "jsdom",
		globals: true,
	},
});
