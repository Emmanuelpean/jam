// @ts-check
"use strict";

const esbuild = require("esbuild");
const { copyFileSync, mkdirSync, readdirSync, statSync } = require("fs");
const { join } = require("path");

mkdirSync("dist", { recursive: true });

esbuild.buildSync({
	entryPoints: ["src/content.ts", "src/popup.ts"],
	outdir: "dist",
	bundle: true,
	format: "iife",
	sourcemap: true,
	target: "es2020",
});

copyFileSync("src/manifest.json", "dist/manifest.json");
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
