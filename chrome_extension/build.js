// @ts-check
"use strict";

const esbuild = require("esbuild");
const { copyFileSync, mkdirSync, readdirSync, readFileSync, writeFileSync, statSync } = require("fs");
const { join } = require("path");

const isProd = process.env.NODE_ENV === "production";
const frontendUrl = isProd ? "https://emmanuelpean.me/jam" : "http://localhost:3000/jam";

mkdirSync("dist", { recursive: true });

esbuild.buildSync({
	entryPoints: ["src/content.ts", "src/popup.ts", "src/jam_bridge.ts"],
	outdir: "dist",
	bundle: true,
	format: "iife",
	sourcemap: true,
	target: "es2020",
	define: {
		__FRONTEND_URL__: JSON.stringify(frontendUrl),
	},
});

const manifest = JSON.parse(readFileSync("src/manifest.json", "utf8"));
manifest.host_permissions.push(`${frontendUrl}/*`);
manifest.content_scripts.push({
	matches: [`${frontendUrl}/*`],
	js: ["jam_bridge.js"],
	run_at: "document_idle",
});
writeFileSync("dist/manifest.json", JSON.stringify(manifest, null, "\t"));
copyFileSync("src/popup.html", "dist/popup.html");

function copyDir(src, dest) {
	mkdirSync(dest, { recursive: true });
	for (const entry of readdirSync(src)) {
		const srcPath = join(src, entry);
		const destPath = join(dest, entry);
		if (statSync(srcPath).isDirectory()) {
			copyDir(srcPath, destPath);
		} else {
			copyFileSync(srcPath, destPath);
		}
	}
}
copyDir("src/icons", "dist/icons");

console.log("Build complete → dist/");
