"use strict";

// ---------------------------------------------------------------------------
// Selector helpers
// ---------------------------------------------------------------------------

function queryFirst(selectors) {
	for (const sel of selectors) {
		const el = document.querySelector(sel);
		if (el && el.textContent.trim()) return el.textContent.trim();
	}
	return null;
}

// ---------------------------------------------------------------------------
// Salary parsing
// ---------------------------------------------------------------------------

// var (not const) so re-injection doesn't throw a redeclaration error.
const SALARY_RE =
	/([£$€¥₹])\s*([\d,]+(?:\.\d+)?)\s*([kKmM]?)\s*(?:\/\w+)?\s*(?:[-–—]|to)\s*[£$€¥₹]?\s*([\d,]+(?:\.\d+)?)\s*([kKmM]?)/;

const CURRENCY_SYMBOLS = { "£": "GBP", $: "USD", "€": "EUR", "¥": "JPY", "₹": "INR" };

function parseNumber(raw) {
	return parseFloat(raw.replace(/,/g, ""));
}

function applyMultiplier(num, suffix) {
	const s = (suffix || "").toLowerCase();
	if (s === "k") return num * 1_000;
	if (s === "m") return num * 1_000_000;
	return num;
}

function parseSalary(text) {
	if (!text) return {};
	const match = text.match(SALARY_RE);
	if (!match) return {};

	const currency = CURRENCY_SYMBOLS[match[1]] || match[1];
	const numA = applyMultiplier(parseNumber(match[2]), match[3]);
	const numB = applyMultiplier(parseNumber(match[4]), match[5]);

	return {
		salary_min: Math.min(numA, numB),
		salary_max: Math.max(numA, numB),
		salary_currency: currency,
	};
}

// ---------------------------------------------------------------------------
// Attendance type mapping (shared by LinkedIn and Indeed scrapers)
// ---------------------------------------------------------------------------

const ATTENDANCE_MAP = [
	{ re: /^remote$/i, value: "remote" },
	{ re: /^hybrid$/i, value: "hybrid" },
	{ re: /^on[\s-]?site$/i, value: "on-site" },
	{ re: /\bremote\b/i, value: "remote" },
	{ re: /\bhybrid\b/i, value: "hybrid" },
	{ re: /\bon[\s-]?site\b/i, value: "on-site" },
];

// ---------------------------------------------------------------------------
// Description extraction — preserves structure lost by textContent/innerText
// ---------------------------------------------------------------------------

const BLOCK_TAGS = new Set(["p", "div", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6", "tr"]);
const LIST_TAGS = new Set(["ul", "ol"]);

function descriptionToText(el) {
	let out = "";

	function walk(node) {
		if (node.nodeType === Node.TEXT_NODE) {
			out += node.textContent;
			return;
		}
		if (node.nodeType !== Node.ELEMENT_NODE) return;

		const tag = node.tagName.toLowerCase();

		if (tag === "br") {
			out += "\n";
			return;
		}

		// Skip LinkedIn's "About the job" section header
		if (/^h[1-6]$/.test(tag) && node.textContent.trim() === "About the job") return;

		if (tag === "li") out += "- ";
		if (LIST_TAGS.has(tag)) out += "\n";

		for (const child of node.childNodes) walk(child);

		if (BLOCK_TAGS.has(tag)) out += "\n";
		if (LIST_TAGS.has(tag)) out += "\n";
	}

	walk(el);

	return out
		.replace(/[ \t]+/g, " ") // collapse inline whitespace
		.replace(/ *\n */g, "\n") // strip spaces around newlines (indentation artifacts)
		.replace(/\n{3,}/g, "\n\n") // max one blank line between blocks
		.replace(/^(- .+)\n\n+(?=- )/gm, "$1\n") // no blank lines between bullets
		.trim();
}

// ---------------------------------------------------------------------------
// Scraper dispatcher — selects scraper based on current hostname
// ---------------------------------------------------------------------------

function scrapeJob() {
	if (window.location.hostname.endsWith("indeed.com")) return scrapeIndeedJob();
	return scrapeLinkedInJob();
}

// Expose shared helpers to window so subsequent execute_script calls can use them
window.ATTENDANCE_MAP = ATTENDANCE_MAP;
window.parseSalary = parseSalary;
window.descriptionToText = descriptionToText;
window.queryFirst = queryFirst;

// ---------------------------------------------------------------------------
// SPA navigation + message handler — registered only once per tab
// ---------------------------------------------------------------------------

if (!window.__jamInjected) {
	window.__jamInjected = true;

	function waitForJobTitle(callback, maxWaitMs = 8000, intervalMs = 200) {
		const start = Date.now();
		const timer = setInterval(() => {
			const title = queryFirst([
				// LinkedIn
				"job-details-jobs-unified-top-card__job-title",
				".jobs-unified-top-card__job-title h1",
				".t-24.t-bold.inline h1",
				"h1.t-24",
				// Indeed
				"[data-testid='jobsearch-JobInfoHeader-title']",
				"h1[class*='jobTitle']",
				// General fallback
				"h1",
			]);
			if (title) {
				clearInterval(timer);
				callback();
			} else if (Date.now() - start >= maxWaitMs) {
				clearInterval(timer);
				callback(); // attempt anyway
			}
		}, intervalMs);
	}

	// noinspection JSUnresolvedReference,JSDeprecatedSymbols
	chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
		// noinspection JSUnresolvedReference
		if (message.action === "scrapeJob") {
			waitForJobTitle(() => {
				try {
					const data = scrapeJob();
					if (!data.title) {
						sendResponse({ success: false, error: "Could not find job title on this page." });
					} else {
						sendResponse({ success: true, data });
					}
				} catch (e) {
					sendResponse({ success: false, error: e.message });
				}
			});
			return true; // keep message channel open for async sendResponse
		}
	});
}
