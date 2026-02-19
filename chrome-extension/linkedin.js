"use strict";

// ---------------------------------------------------------------------------
// LinkedIn scraper
// Depends on shared globals defined in content.js:
//   ATTENDANCE_MAP, parseSalary, descriptionToText, queryFirst
// ---------------------------------------------------------------------------

function getFitLevelTexts() {
	const container = document.querySelector("div.job-details-fit-level-preferences");
	if (!container) return [];
	return Array.from(
		container.querySelectorAll("button.artdeco-button.artdeco-button--secondary.artdeco-button--muted")
	).map((btn) => btn.textContent.trim());
}

function findSalaryText() {
	// Salary may appear in the tertiary description or insight items
	const salarySelectors = [
		".compensation__salary",
		"[class*='salary']",
		".job-details-jobs-unified-top-card__job-insight--highlight span",
		".job-details-jobs-unified-top-card__salary-main-rail",
	];
	for (const sel of salarySelectors) {
		const el = document.querySelector(sel);
		if (el) {
			const text = el.textContent.trim();
			if (text) return text;
		}
	}
	// Fall back: any element whose text looks like a salary range
	const allText = document.querySelectorAll(
		".job-details-jobs-unified-top-card__tertiary-description-container span"
	);
	for (const el of allText) {
		const text = el.textContent.trim();
		if (/[£$€¥₹]/.test(text) && /[-–—]|to/.test(text)) return text;
	}
	return null;
}

function getTopCardChips() {
	// Insight chips in the top-card tertiary section (location, work type, etc.)
	return Array.from(
		document.querySelectorAll(
			".job-details-jobs-unified-top-card__tertiary-description-container .job-details-jobs-unified-top-card__job-insight-view-model-secondary"
		)
	).map((el) => el.textContent.trim());
}

function parseLinkedInLocationAndAttendance() {
	// Location: first span.tvm__text--low-emphasis inside the tertiary container
	let location = null;
	const locEl = document.querySelector(
		"div.t-black--light.mt2.job-details-jobs-unified-top-card__tertiary-description-container span.tvm__text.tvm__text--low-emphasis"
	);
	if (locEl) location = locEl.textContent.trim() || null;

	// Attendance: buttons inside .job-details-fit-level-preferences
	let attendance_type = null;
	const fitTexts = getFitLevelTexts();
	for (const text of fitTexts) {
		for (const entry of ATTENDANCE_MAP) {
			if (entry.re.test(text)) {
				attendance_type = entry.value;
				break;
			}
		}
		if (attendance_type) break;
	}

	// Fallback: scan tertiary chips for attendance keywords
	if (!attendance_type) {
		for (const chip of getTopCardChips()) {
			for (const entry of ATTENDANCE_MAP) {
				if (entry.re.test(chip)) {
					attendance_type = entry.value;
					break;
				}
			}
			if (attendance_type) break;
		}
	}

	return { location, attendance_type };
}

function cleanLinkedInUrl() {
	try {
		const u = new URL(window.location.href);
		// /jobs/view/<id>/... → keep only the canonical path
		const match = u.pathname.match(/\/jobs\/view\/(\d+)/);
		if (match) return `https://www.linkedin.com/jobs/view/${match[1]}/`;

		// /jobs/collections/...?currentJobId=<id>
		const jobId = u.searchParams.get("currentJobId");
		if (jobId) return `https://www.linkedin.com/jobs/view/${jobId}/`;
	} catch (_) {}
	return window.location.href;
}

function scrapeLinkedInJob() {
	const title = queryFirst([
		".job-details-jobs-unified-top-card__job-title h1",
		".jobs-unified-top-card__job-title h1",
		".t-24.t-bold.inline h1",
		"h1.t-24",
		"h1",
	]);

	const company = queryFirst([
		".job-details-jobs-unified-top-card__company-name a",
		".job-details-jobs-unified-top-card__company-name",
		".jobs-unified-top-card__company-name a",
		".jobs-unified-top-card__company-name",
		".topcard__org-name-link",
		".topcard__flavor--black-link",
	]);

	const descEl = document.querySelector(
		"div.jobs-description-content__text, div.jobs-box__html-content, div#job-details"
	);
	const description = descEl ? descriptionToText(descEl) : null;

	const url = cleanLinkedInUrl();

	const { location, attendance_type } = parseLinkedInLocationAndAttendance();

	const salary = parseSalary(findSalaryText());

	return {
		title,
		company,
		description,
		url,
		platform: "linkedin",
		location,
		attendance_type,
		...salary,
	};
}

// Expose to window so Selenium execute_script can call it across injection boundaries
window.scrapeLinkedInJob = scrapeLinkedInJob;
