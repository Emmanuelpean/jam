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
	deadline?: string | null;
}

interface ScrapeResponse {
	success: boolean;
	data?: ScrapedJob;
	error?: string;
}

interface Window {
	__jamInjected?: boolean;
	scrapeLinkedInJob: () => ScrapedJob;
	scrapeIndeedJob: () => ScrapedJob;
	scrapeNhsJob: () => ScrapedJob;
	scrapeVeganJobsJob: () => ScrapedJob;
}
