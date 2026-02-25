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
	// Title
	const title: string | null = queryFirst([
		'[data-testid="jobsearch-JobInfoHeader-title"]',
		"h1[class*='jobTitle']",
		"h1",
	]);

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

	// Location
	const location: string | null = queryFirst([
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
		const text: string = el.textContent?.trim() ?? "";
		for (const entry of ATTENDANCE_MAP) {
			if (entry.re.test(text)) {
				attendance_type = entry.value;
				break;
			}
		}
		if (attendance_type) break;
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
