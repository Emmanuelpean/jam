"use strict";

// ---------------------------------------------------------------------------
// Indeed scraper
// Depends on shared globals defined in content.ts:
//   ATTENDANCE_MAP, parseSalary, descriptionToText, queryFirst
// ---------------------------------------------------------------------------

function cleanIndeedUrl(): string {
	try {
		const u = new URL(window.location.href);
		// Canonical /viewjob page — keep jk param only
		const jk = u.searchParams.get("jk") || u.searchParams.get("vjk");
		if (jk) return `https://www.indeed.com/viewjob?jk=${jk}`;
	} catch (_) {}
	return window.location.href;
}

function scrapeIndeedJob(): ScrapedJob {
	const title = window.queryFirst(['[data-testid="jobsearch-JobInfoHeader-title"]', "h1[class*='jobTitle']", "h1"]);

	const company = window.queryFirst([
		"[data-testid='inlineHeader-companyName'] a",
		"[data-testid='inlineHeader-companyName']",
		"[data-testid='jobsearch-JobInfoHeader-companyName'] a",
		"[data-testid='jobsearch-JobInfoHeader-companyName']",
		".jobsearch-CompanyInfoWithoutHeaderImage a[data-tn-element='reviewsLink']",
	]);

	const descEl = document.querySelector("[data-testid='jobsearch-jobDescriptionText'], #jobDescriptionText");
	const description = descEl ? window.descriptionToText(descEl) : null;

	const url = cleanIndeedUrl();

	const location = window.queryFirst([
		"[data-testid='inlineHeader-companyLocation']",
		"[data-testid='jobsearch-JobInfoHeader-companyLocation']",
		".jobsearch-JobInfoHeader-subtitle [data-testid]",
	]);

	// Attendance type from job type/remote label
	let attendance_type: string | null = null;
	const jobTypeEls = document.querySelectorAll(
		"[data-testid='attribute_snippet_testid'], .css-k5flys, [class*='jobType'], [class*='remote']"
	);
	for (const el of jobTypeEls) {
		const text = el.textContent?.trim() ?? "";
		for (const entry of window.ATTENDANCE_MAP) {
			if (entry.re.test(text)) {
				attendance_type = entry.value;
				break;
			}
		}
		if (attendance_type) break;
	}

	// Salary
	const salaryText = window.queryFirst([
		"[data-testid='attribute_snippet_testid']",
		"[class*='salary']",
		"#salaryInfoAndJobType span",
	]);
	const salary = window.parseSalary(salaryText);

	return {
		title,
		company,
		description,
		url,
		platform: "indeed",
		location,
		attendance_type,
		...salary,
	};
}

// Expose to window so Selenium execute_script can call it across injection boundaries
window.scrapeIndeedJob = scrapeIndeedJob;
