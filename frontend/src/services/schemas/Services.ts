import { BaseOut, GeoLocationData, OwnedOut } from "./Base";

export enum ProcessingStatus {
	PENDING = "pending",
	COMPLETED = "completed",
	FAILED = "failed",
	SKIPPED = "skipped",
	FILTERED = "filtered",
}

export interface ServiceLog extends BaseOut {
	run_datetime: Date;
	run_duration: number | null;
	is_finished: boolean;
	is_success: boolean;
}

// ---------------------------------------------------- JOB SCRAPING ---------------------------------------------------

export interface JobScrapingServiceLogData extends ServiceLog {
	user_found_ids: number[];
	user_processed_ids: number[];
	emails: number[];
	scraped_jobs: ScrapedJobData[];
	platform_stats: PlatformStat[];
	job_to_process_n: number;
	job_scrape_succeeded_n: number;
	job_scrape_failed_n: number;
	job_scrape_copied_n: number;
	job_scrape_skipped_n: number;
	job_found_n: number;
	email_found_n: number;
	email_saved_n: number;
	email_skipped_n: number;
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

export interface ServiceError extends BaseOut {
	error_type: string;
	message: string;
	context: Record<string, unknown> | null;
	traceback: string;
	is_acknowledged: boolean;
	level: string | null;
	scraped_job_id: number | null;
	job_rating_id: number | null;
	job_email_scraping_service_log_id: number | null;
	job_rating_service_log_id: number | null;
	provider_monitoring_service_log_id: number | null;
}

// ---------------------------------------------------- SCRAPED JOB ----------------------------------------------------

export interface ScrapedJobData extends OwnedOut {
	external_job_id: string;
	status: ProcessingStatus;
	skip_reason: string | null;
	scrape_datetime: Date;
	scraping_retry_count: number;
	scraping_next_retry_at: string | null;
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
	location: string | null;
	attendance_type: string | null;
	raw_location: string | null;
	emails: number[];
	job_rating: JobRatingData | null;
	geolocation: GeoLocationData | null;
	scraping_errors: ServiceError[];
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
	status: ProcessingStatus;
	skip_reason: string | null;
	scraped_job_id: number | null;
	user_qualification_id: number | null;
	job_prompt_template_id: number | null;
	system_prompt_id: number | null;
	job_prompt: string | null;
	notes: string[];
	rating_retry_count: number;
	rating_next_retry_at: string | null;
	rating_errors: ServiceError[];
}

export interface ScrapingFilterTransform {
	type: string;
	operator: string;
	value: string;
	case_sensitive: boolean;
}

export type FilterVariant = "exclusion" | "favourite";

export interface ScrapingFilterData extends OwnedOut {
	type: string;
	operator: string;
	value: string;
	case_sensitive: boolean;
	is_active: boolean;
	filtered_jobs: number[];
}

export interface ScrapingFilterCreate {
	type: string;
	operator: string;
	value: string;
	case_sensitive: boolean;
	is_tour?: boolean;
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

// ------------------------------------------------ PROVIDER MONITORING ------------------------------------------------

export interface AnthropicDailyUsageData extends BaseOut {
	date: string;
	usage_usd: number;
}

export interface ApifyDailyUsageData extends BaseOut {
	date: string;
	usage_usd: number;
}

export interface ApifyBalanceData extends BaseOut {
	limit_usd: number | null;
}

export interface BrightdataDailyUsageData extends BaseOut {
	date: string;
	dataset: string;
	usage_usd: number;
}

export interface BrightdataBalanceData extends BaseOut {
	balance_usd: number | null;
	pending_costs_usd: number | null;
}

export interface StripeDailyIncomeData extends BaseOut {
	date: string;
	gross_gbp: number;
	net_gbp: number;
}
