import { BaseOut, GeoLocationData, OwnedOut } from "./Base";

export interface ServiceLog extends BaseOut {
	run_datetime: Date;
	run_duration: number | null;
	is_success: boolean | null;
	error_message: string | null;
}

// ---------------------------------------------------- JOB SCRAPING ---------------------------------------------------

export interface JobScrapingServiceLogData extends ServiceLog {
	user_found_ids: number[];
	user_processed_ids: number[];
	emails: number[];
	scraped_jobs: ScrapedJobData[];
	platform_stats: PlatformStat[];
	errors: ServiceError[];
	job_to_process_n: number;
	job_scrape_succeeded_n: number;
	job_scrape_failed_n: number;
	job_scrape_copied_n: number;
	job_scrape_skipped_n: number;
	job_found_n: number;
	email_found_n: number;
	email_saved_n: number;
	email_skipped_n: number;
	service_errors: ServiceError[];
}

export interface JobRatingServiceLogData extends ServiceLog {
	job_found_ids: number[];
	job_succeeded_ids: number[];
	job_failed_ids: number[];
	job_skipped_ids: number[];
	user_found_ids: number[];
	user_processed_ids: number[];
}

export interface PlatformStat {
	id: number;
	name: string;
	email_saved_ids: number[];
	email_skipped_ids: number[];
	job_found_ids: number[];
	job_to_process_ids: number[];
	job_scrape_failed_ids: number[];
	job_scrape_succeeded_ids: number[];
	job_scrape_copied_ids: number[];
	job_scrape_skipped_ids: number[];
	service_log_id: number;
}

export interface ServiceError {
	id: number;
	error_type: string;
	message: string;
	traceback: string;
	service_log_id: number;
}

// ---------------------------------------------------- SCRAPED JOB ----------------------------------------------------

export interface ScrapedJobData extends OwnedOut {
	external_job_id: string;
	is_scraped: boolean;
	is_failed: boolean;
	is_processed: boolean;
	is_skipped: boolean;
	skip_reason: string | null;
	scrape_error: Array<{ datetime: string; error: string }>;
	scrape_datetime: Date;
	retry_count: number;
	next_retry_at: string | null;
	is_active: boolean;
	is_imported: boolean;
	title: string | null;
	description: string | null;
	salary_min: number | null;
	salary_max: number | null;
	salary_currency: string | null;
	platform: string | null;
	is_closed: boolean;
	url: string | null;
	deadline: Date | null;
	company: string | null;
	location_postcode: string | null;
	location_city: string | null;
	location_country: string | null;
	parsed_location: string | null;
	attendance_type: string | null;
	location: string | null;
	emails: number[];
	job_rating: JobRatingData | null;
	geolocation: GeoLocationData | null;
	read_at: Date | null;
}

export interface ScrapedJobUpdate {
	is_imported?: boolean;
	read_at?: string | null;
}

export interface JobRatingData extends BaseOut {
	overall_score: number | null;
	technical_score: number | null;
	experience_score: number | null;
	educational_score: number | null;
	interest_score: number | null;
	feedback: string | null;
	is_success: boolean | null;
	is_skipped: boolean | null;
	skip_reason: string | null;
	error: string | null;
	scraped_job_id: number | null;
	user_qualification_id: number | null;
	job_prompt_template_id: number | null;
	system_prompt_id: number | null;
	job_prompt: string | null;
	notes: string[];
}

export interface ScrapingFilterTransform {
	type: string;
	operator: string;
	value: string;
	case_sensitive: boolean;
}

export interface ScrapingFilterData extends OwnedOut {
	type: string;
	operator: string;
	value: string;
	case_sensitive: boolean;
	is_active: boolean;
	filtered_jobs: number[];
}

// ----------------------------------------------------- JOB EMAIL -----------------------------------------------------

export interface JobEmailData extends OwnedOut {
	external_email_id: string | null;
	subject: string | null;
	sender: string | null;
	date_received: Date | null;
	platform: string | null;
	body: string | null;
	service_log_id: number | null;
	job_found_n: number;
	alert_name: string | null;
	jobs: number[];
}

// ------------------------------------------- FORWARDING CONFIRMATION LINK -------------------------------------------

export interface ForwardingConfirmationLinkData extends OwnedOut {
	url: string;
	platform: string;
	is_used: boolean;
}

// ---------------------------------------------------- AI PROMPTS ----------------------------------------------------

export interface AiSystemPromptData extends BaseOut {
	prompt: string;
}
