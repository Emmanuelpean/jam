"use strict";

// Guard against double-injection on already-open tabs.
if (window.__jamInjected) {
	/* already loaded — skip */
} else {
	window.__jamInjected = true;

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

	// Captures the multiplier suffix (K/M) as its own group so it is never
	// confused with letters elsewhere in the text (e.g. "United Kingdom").
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

	// Returns text content of all fit-level-preference buttons (salary, attendance, etc.)
	function getFitLevelTexts() {
		const container = document.querySelector(".job-details-fit-level-preferences");
		if (!container) return [];
		return Array.from(container.querySelectorAll("button"))
			.map((b) => b.textContent.trim())
			.filter(Boolean);
	}

	// Scan fit-level buttons then fallback to insight elements for a salary range.
	function findSalaryText() {
		// Primary: fit-level preference buttons (newest LinkedIn layout)
		for (const t of getFitLevelTexts()) {
			if (/[£$€¥₹]/.test(t) && /[-–—]/.test(t)) return t;
		}

		// Secondary: dedicated salary elements
		const dedicated = queryFirst([
			".compensation__salary",
			".compensation-v2-card__salary-range",
			'[class*="compensation"][class*="range"]',
		]);
		if (dedicated) return dedicated;

		// Fallback: scan insight list items for a currency-range pattern
		const candidates = document.querySelectorAll(
			".job-details-jobs-unified-top-card__job-insight," +
				".jobs-unified-top-card__job-insight," +
				'li[class*="insight"],' +
				'[class*="insight-item"]'
		);
		for (const el of candidates) {
			const t = el.textContent.trim();
			if (/[£$€¥₹]/.test(t) && /[-–—]/.test(t)) return t;
		}
		return null;
	}

	// ---------------------------------------------------------------------------
	// Top-card chip splitting (location + attendance type)
	//
	// LinkedIn renders the job metadata as a single text block separated by
	// middle-dot (·) bullets, e.g.:
	//   "Acme Corp · London, United Kingdom · Hybrid · 1,001–5,000 employees"
	// Splitting on · lets us classify each chip independently.
	// ---------------------------------------------------------------------------

	const ATTENDANCE_MAP = [
		{ re: /^remote$/i, value: "remote" },
		{ re: /^hybrid$/i, value: "hybrid" },
		{ re: /^on[\s-]?site$/i, value: "on-site" },
		{ re: /\bremote\b/i, value: "remote" },
		{ re: /\bhybrid\b/i, value: "hybrid" },
		{ re: /\bon[\s-]?site\b/i, value: "on-site" },
	];

	function getTopCardChips() {
		const selectors = [
			".job-details-jobs-unified-top-card__primary-description-container",
			".jobs-unified-top-card__primary-description",
			".job-details-jobs-unified-top-card__subtitle",
			".jobs-unified-top-card__subtitle-primary-grouping",
			// broad fallback
			'[class*="top-card__primary-description"]',
			'[class*="unified-top-card__subtitle"]',
		];
		for (const sel of selectors) {
			const el = document.querySelector(sel);
			if (el && el.textContent.trim()) {
				return el.textContent
					.trim()
					.split(/\s*·\s*/)
					.map((s) => s.trim())
					.filter(Boolean);
			}
		}
		return [];
	}

	function parseLocationAndAttendance() {
		let location_city = null;
		let location_country = null;
		let attendance_type = null;

		// Primary: fit-level preference buttons (newest LinkedIn layout)
		for (const t of getFitLevelTexts()) {
			if (!attendance_type) {
				for (const { re, value } of ATTENDANCE_MAP) {
					if (re.test(t)) {
						attendance_type = value;
						break;
					}
				}
			}
		}

		// Location + attendance fallback: top-card ·-separated chips
		const chips = getTopCardChips();
		for (const chip of chips) {
			if (!attendance_type) {
				for (const { re, value } of ATTENDANCE_MAP) {
					if (re.test(chip)) {
						attendance_type = value;
						break;
					}
				}
				if (attendance_type) continue;
			}

			// Location — chip that contains a comma and looks geographic
			// (skip chips that are purely numeric like employee counts)
			if (!location_city && chip.includes(",") && !/^\d/.test(chip)) {
				const parts = chip
					.split(",")
					.map((p) => p.trim())
					.filter(Boolean);
				location_city = parts[0];
				location_country = parts[parts.length - 1];
			}
		}

		// Last resort: attendance keyword embedded in location text
		// e.g. "London, United Kingdom (Hybrid)"
		if (!attendance_type && (location_city || location_country)) {
			const combined = [location_city, location_country].join(" ");
			for (const { re, value } of ATTENDANCE_MAP) {
				if (re.test(combined)) {
					attendance_type = value;
					break;
				}
			}
		}

		return { location_city, location_country, attendance_type };
	}

	// ---------------------------------------------------------------------------
	// Description extraction — preserves structure lost by textContent/innerText
	// ---------------------------------------------------------------------------

	// Block-level tags that should produce a newline after their content.
	const BLOCK_TAGS = new Set(['p', 'div', 'li', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'tr']);
	// List container tags that add an extra blank line around the list.
	const LIST_TAGS  = new Set(['ul', 'ol']);

	function descriptionToText(el) {
		let out = '';

		function walk(node) {
			if (node.nodeType === Node.TEXT_NODE) {
				out += node.textContent;
				return;
			}
			if (node.nodeType !== Node.ELEMENT_NODE) return;

			const tag = node.tagName.toLowerCase();

			if (tag === 'br') { out += '\n'; return; }
			if (tag === 'li') out += '- ';
			if (LIST_TAGS.has(tag)) out += '\n';

			for (const child of node.childNodes) walk(child);

			if (BLOCK_TAGS.has(tag)) out += '\n';
			if (LIST_TAGS.has(tag))  out += '\n';
		}

		walk(el);

		return out
			.replace(/[ \t]+/g, ' ')       // collapse inline whitespace
			.replace(/\n{3,}/g, '\n\n')     // max one blank line between blocks
			.trim();
	}

	// ---------------------------------------------------------------------------
	// URL cleanup
	// ---------------------------------------------------------------------------

	function cleanUrl(href) {
		try {
			const u = new URL(href);
			// Collections page: /jobs/collections/...?currentJobId=1234 → canonical view URL
			const jobId = u.searchParams.get("currentJobId");
			if (jobId && u.pathname.includes("/jobs/collections")) {
				return `${u.origin}/jobs/view/${jobId}/`;
			}
			// Standard view page: strip query params
			return u.origin + u.pathname;
		} catch (_) {
			return href;
		}
	}

	// ---------------------------------------------------------------------------
	// Main scraper
	// ---------------------------------------------------------------------------

	function scrapeJob() {
		const title = queryFirst([
			"h1.job-details-jobs-unified-top-card__job-title",
			"h1.t-24.t-bold.inline",
			'h1[class*="job-title"]',
			".job-details-jobs-unified-top-card__job-title h1",
			"h1",
		]);

		const company_name = queryFirst([
			".job-details-jobs-unified-top-card__company-name a",
			".job-details-jobs-unified-top-card__company-name",
			'[class*="company-name"]',
			".topcard__org-name-link",
		]);

		const description = (() => {
			const selectors = [
				".jobs-description-content__text",
				".jobs-description__content",
				"#job-details",
				".jobs-box__html-content",
			];
			for (const sel of selectors) {
				const el = document.querySelector(sel);
				if (el && el.textContent.trim()) {
					return descriptionToText(el).replace(/^About the job\s*/i, "").trimStart();
				}
			}
			return null;
		})();

		const salary = parseSalary(findSalaryText());
		const locationAndAttendance = parseLocationAndAttendance();
		const url = cleanUrl(window.location.href);

		return {
			title,
			company_name: company_name || null,
			description: description || null,
			url,
			...locationAndAttendance,
			...salary,
		};
	}

	// ---------------------------------------------------------------------------
	// SPA navigation — wait for a non-empty h1 before scraping
	// ---------------------------------------------------------------------------

	function waitForJobTitle(callback, maxWaitMs = 8000, intervalMs = 200) {
		const start = Date.now();
		const timer = setInterval(() => {
			const h1 = document.querySelector("h1");
			if (h1 && h1.textContent.trim()) {
				clearInterval(timer);
				callback();
			} else if (Date.now() - start >= maxWaitMs) {
				clearInterval(timer);
				callback(); // attempt anyway
			}
		}, intervalMs);
	}

	// ---------------------------------------------------------------------------
	// Message handler
	// ---------------------------------------------------------------------------

	chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
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
} // end injection guard
