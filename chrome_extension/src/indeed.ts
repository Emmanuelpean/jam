import { queryFirst, parseSalary, descriptionToText, ATTENDANCE_MAP } from "./utils";

function cleanIndeedUrl(): string {
	try {
		const u = new URL(window.location.href);
		const jk: string | null = u.searchParams.get("jk") || u.searchParams.get("vjk");
		if (jk) return `https://www.indeed.com/viewjob?jk=${jk}`;
	} catch (_) {}
	return window.location.href;
}

export function scrapeIndeedJob(): ScrapedJob {
	// Title — strip Indeed's " - job post" suffix if present
	const rawTitle: string | null = queryFirst([
		'[data-testid="jobsearch-JobInfoHeader-title"]',
		"h1[class*='jobTitle']",
		"h1",
	]);
	const title: string | null = rawTitle ? rawTitle.replace(/\s*-\s*job post\s*$/i, "") : null;

	// Company
	const company: string | null = queryFirst([
		"[data-testid='inlineHeader-companyName'] a",
		"[data-testid='inlineHeader-companyName']",
		"[data-testid='jobsearch-JobInfoHeader-companyName'] a",
		"[data-testid='jobsearch-JobInfoHeader-companyName']",
		".jobsearch-CompanyInfoWithoutHeaderImage a[data-tn-element='reviewsLink']",
	]);

	// Description
	const descEl: Element | null = document.querySelector(
		"[data-testid='jobsearch-jobDescriptionText'], #jobDescriptionText"
	);
	const description: string | null = descEl ? descriptionToText(descEl) : null;

	// URL
	const url: string = cleanIndeedUrl();

	// Location + attendance: Indeed encodes both in a single element, e.g. "Coleshill•Remote"
	// Split on middle dot (·) or bullet (•) — first part is location, rest checked for attendance.
	const locationSelectors = [
		"[data-testid='inlineHeader-companyLocation']",
		"[data-testid='jobsearch-JobInfoHeader-companyLocation']",
		".jobsearch-JobInfoHeader-subtitle [data-testid]",
	];
	let locationRaw: string | null = null;
	for (const sel of locationSelectors) {
		const text = document.querySelector(sel)?.textContent?.trim();
		if (text) { locationRaw = text; break; }
	}
	const locationParts = (locationRaw ?? "").split(/[\u00b7\u2022]/).map((s) => s.trim());
	const location: string | null = locationParts[0] || null;

	let attendance_type: string | null = null;
	for (const part of locationParts.slice(1)) {
		for (const entry of ATTENDANCE_MAP) {
			if (entry.re.test(part)) { attendance_type = entry.value; break; }
		}
		if (attendance_type) break;
	}

	// Fallback: scan job-type / remote label elements
	if (!attendance_type) {
		for (const el of document.querySelectorAll(
			"[data-testid='attribute_snippet_testid'], .css-k5flys, [class*='jobType'], [class*='remote']"
		)) {
			const text: string = el.textContent?.trim() ?? "";
			for (const entry of ATTENDANCE_MAP) {
				if (entry.re.test(text)) { attendance_type = entry.value; break; }
			}
			if (attendance_type) break;
		}
	}

	// Salary
	const salaryText: string | null = queryFirst([
		"#salaryInfoAndJobType span",
		"[data-testid='jobsearch-OtherJobDetailsContainer'] span",
		"[class*='salary']",
	]);
	const salary: SalaryResult = parseSalary(salaryText);

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
