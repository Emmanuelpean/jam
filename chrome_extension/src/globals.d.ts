// Shared interfaces for scraped job data and window globals shared between content scripts.

interface AttendanceEntry {
	re: RegExp;
	value: string;
}

interface SalaryResult {
	salary_min?: number;
	salary_max?: number;
	salary_currency?: string;
}

interface ScrapedJob extends SalaryResult {
	title: string | null;
	company: string | null;
	description: string | null;
	url: string;
	platform: string;
	location: string | null;
	attendance_type: string | null;
	application_status?: string | null;
}

interface ScrapeResponse {
	success: boolean;
	data?: ScrapedJob;
	error?: string;
}

interface Window {
	ATTENDANCE_MAP: AttendanceEntry[];
	parseSalary: (text: string | null) => SalaryResult;
	descriptionToText: (el: Element) => string;
	queryFirst: (selectors: string[]) => string | null;
	scrapeLinkedInJob: () => ScrapedJob;
	scrapeIndeedJob: () => ScrapedJob;
	__jamInjected?: boolean;
}
