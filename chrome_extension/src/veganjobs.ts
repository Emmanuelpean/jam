import { descriptionToText, ATTENDANCE_MAP } from "./utils";

// ---------------------------------------------------------------------------
// VeganJobs scraper (veganjobs.com)
// ---------------------------------------------------------------------------

function cleanVeganJobsUrl(): string {
	const match = window.location.pathname.match(/\/job\/([^/]+)/);
	if (match) return `https://veganjobs.com/job/${match[1]}`;
	return window.location.href;
}

function getText(selector: string): string | null {
	return document.querySelector(selector)?.textContent?.trim() || null;
}

function parseAttendanceFromJsonLd(): string | null {
	try {
		const script = document.querySelector('script[type="application/ld+json"]');
		if (!script?.textContent) return null;
		const data = JSON.parse(script.textContent);
		const locationType: string = data?.jobLocationType ?? "";
		for (const entry of ATTENDANCE_MAP) {
			if (entry.re.test(locationType)) return entry.value;
		}
	} catch (_) {}
	return null;
}

export function scrapeVeganJobsJob(): ScrapedJob {
	const title = getText("h2.page-title");

	const company = getText("div.joblisting-meta-company-name");

	// Location is inside an <a> when it's a real place; plain text when "Remote"
	const locationLiEl = document.querySelector("li.location");
	const locationLink = locationLiEl?.querySelector("a")?.textContent?.trim() || null;
	const locationRaw = locationLiEl?.textContent?.trim() || null;

	// If the text matches a known attendance pattern (e.g. "Remote"), treat it
	// as attendance type and leave location null; otherwise keep the city text.
	let location: string | null = locationLink || locationRaw;
	let attendance_type: string | null = null;

	for (const entry of ATTENDANCE_MAP) {
		if (entry.re.test(locationRaw ?? "")) {
			attendance_type = entry.value;
			location = null;
			break;
		}
	}

	// Fall back to JSON-LD jobLocationType if not already resolved
	if (!attendance_type) {
		attendance_type = parseAttendanceFromJsonLd();
	}

	// Description: main job listing content
	const descEl = document.querySelector<Element>("div.job_listing-description");
	const description = descEl ? descriptionToText(descEl) : null;

	return {
		title,
		company,
		description,
		url: cleanVeganJobsUrl(),
		platform: "veganjobs",
		location,
		attendance_type,
	};
}
