import { parseSalary, descriptionToText, ATTENDANCE_MAP } from "./utils";

// ---------------------------------------------------------------------------
// NHS Jobs scraper (www.jobs.nhs.uk)
// ---------------------------------------------------------------------------

function cleanNhsUrl(): string {
	const match = window.location.pathname.match(/\/candidate\/jobadvert\/([^/]+)/);
	if (match) return `https://www.jobs.nhs.uk/candidate/jobadvert/${match[1]}`;
	return window.location.href;
}

function getText(selector: string): string | null {
	return document.querySelector(selector)?.textContent?.trim() || null;
}

const MONTH_MAP: Record<string, string> = {
	January: "01", February: "02", March: "03", April: "04",
	May: "05", June: "06", July: "07", August: "08",
	September: "09", October: "10", November: "11", December: "12",
};

function parseNhsDate(text: string | null): string | null {
	if (!text) return null;
	const match = text.match(/(\d{1,2})\s+(\w+)\s+(\d{4})/);
	if (!match) return null;
	const month = MONTH_MAP[match[2]];
	if (!month) return null;
	return `${match[3]}-${month}-${match[1].padStart(2, "0")}`;
}

export function scrapeNhsJob(): ScrapedJob {
	const title = getText("#heading");

	const company = getText("#employer_name");

	// Location: join non-empty address parts
	const locationParts = [
		"#employer_address_line_1",
		"#employer_address_line_2",
		"#employer_town",
		"#employer_county",
		"#employer_postcode",
	]
		.map((sel) => getText(sel))
		.filter(Boolean) as string[];
	const location = locationParts.join(", ") || null;

	const salary = parseSalary(getText("#range_salary"));

	// Attendance type from working pattern
	let attendance_type: string | null = null;
	const workPatternEl = document.querySelector<HTMLElement>("#working_pattern_heading + p");
	const workPattern = workPatternEl?.textContent?.trim() ?? "";
	for (const entry of ATTENDANCE_MAP) {
		if (entry.re.test(workPattern)) {
			attendance_type = entry.value;
			break;
		}
	}

	// Description: the desktop-visible job description container
	const descEl = document.querySelector<Element>("div.hide-mobile");
	const description = descEl ? descriptionToText(descEl) : null;

	const deadline = parseNhsDate(getText("#closing_date"));

	return {
		title,
		company,
		description,
		url: cleanNhsUrl(),
		platform: "nhs",
		location,
		attendance_type,
		deadline,
		...salary,
	};
}
