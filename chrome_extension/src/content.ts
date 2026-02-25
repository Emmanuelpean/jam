"use strict";

import { queryFirst } from "./utils";
import { scrapeLinkedInJob } from "./linkedin";
import { scrapeIndeedJob } from "./indeed";

// ---------------------------------------------------------------------------
// Scraper dispatcher — selects scraper based on current hostname
// ---------------------------------------------------------------------------

function scrapeJob(): ScrapedJob {
	if (window.location.hostname.endsWith("indeed.com")) return scrapeIndeedJob();
	return scrapeLinkedInJob();
}

// Expose scrapers to window for Selenium test access
window.scrapeLinkedInJob = scrapeLinkedInJob;
window.scrapeIndeedJob = scrapeIndeedJob;

// ---------------------------------------------------------------------------
// SPA navigation + message handler — registered only once per tab
// ---------------------------------------------------------------------------

if (!window.__jamInjected) {
	window.__jamInjected = true;

	function waitForJobTitle(callback: () => void, maxWaitMs = 8000, intervalMs = 200): void {
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
	chrome.runtime.onMessage.addListener((message: { action: string }, _sender, sendResponse) => {
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
					sendResponse({ success: false, error: (e as Error).message });
				}
			});
			return true; // keep message channel open for async sendResponse
		}
	});
}
