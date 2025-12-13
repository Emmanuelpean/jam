interface BaseOut {
	id: number;
	created_at: Date | string;
	modified_at: Date | string;
}

export interface OwnedOut extends BaseOut {
	owner_id: number;
}

// ------------------------------------------------------ SETTING ------------------------------------------------------

export interface SettingDataTransform {
	name: string;
	value: string;
	description?: string;
	is_active: boolean;
}

export interface SettingData extends BaseOut {
	name: string;
	value: string;
	description?: string;
	is_active: boolean;
}

// ------------------------------------------------------- KEYWORD ------------------------------------------------------

export interface KeywordDataTransform {
	name: string;
}

export interface KeywordData extends OwnedOut {
	name: string;
}

// ----------------------------------------------------- AGGREGATOR -----------------------------------------------------

export interface AggregatorDataTransform {
	name: string;
	url: string;
}

export interface AggregatorData extends OwnedOut {
	name: string;
	url: string;
}

// ------------------------------------------------------- COMPANY -----------------------------------------------------

export interface CompanyDataTransform {
	name: string;
	url: string | null;
	description: string | null;
}

export interface CompanyData extends OwnedOut {
	name: string;
	url: string | null;
	description: string | null;
	persons: OwnedOut[];
	jobs: OwnedOut[];
}

// ------------------------------------------------------ LOCATION -----------------------------------------------------

export interface LocationDataTransform {
	city?: string | null;
	postcode?: string | null;
	country?: string | null;
}

export interface LocationData extends OwnedOut {
	city?: string | null;
	postcode?: string | null;
	country?: string | null;
	name: string;
}

// ------------------------------------------------------- PERSON ------------------------------------------------------

export interface PersonTransform {
	first_name: string;
	last_name: string;
	email: string | null;
	phone: string | null;
	linkedin_url: string | null;
	role: string | null;
	company_id: number | null;
}

export interface PersonData extends OwnedOut {
	first_name: string;
	last_name: string;
	name: string;
	email: string | null;
	phone: string | null;
	role: string | null;
	linkedin_url: string | null;
	company_id: number | null;
}

// ----------------------------------------------- JOB APPLICATION UPDATE ----------------------------------------------

export interface JobApplicationUpdateDataTransform {
	date: Date | string;
	type: string;
	job_id: number;
	note: string | null;
}

export interface JobApplicationUpdateData extends OwnedOut {
	date: Date | string;
	type: string;
	job_id: number;
	note: string | null;
}

export interface EnrichedJobApplicationUpdateData extends JobApplicationUpdateData {
	number: number;
}

// -------------------------------------------------------- JOB --------------------------------------------------------

export interface JobDataTransform {
	title: string;
	description: string | null;
	note: string | null;
	url: string | null;
	salary_min: number | null;
	salary_max: number | null;
	salary_currency: string | null;
	personal_rating: number | null;
	deadline: Date | string | null;
	company_id: number | null;
	source_id: number | null;
	location_id: number | null;
	application_date: Date | string | null;
	application_status: string | null;
	applied_via: string | null;
	application_note: string | null;
	application_aggregator_id: number | null;
	application_url: string | null;
	attendance_type: string | null;
	keywords: number[];
	contacts: number[];
}

export interface JobData extends OwnedOut {
	title: string;
	name: string;
	description: string | null;
	note: string | null;
	url: string | null;
	salary_min: number | null;
	salary_max: number | null;
	salary_currency: string | null;
	personal_rating: number | null;
	deadline: Date | string | null;
	company_id: number | null;
	source_id: number | null;
	location_id: number | null;
	followup_snooze_datetime: Date | string | null;
	application_date: Date | string | null;
	application_status: string | null;
	applied_via: string | null;
	application_note: string | null;
	application_aggregator_id: number | null;
	application_url: string | null;
	attendance_type: string | null;
	keywords: number[];
	contacts: number[];
}

export interface EnrichedJobData extends JobData {
	last_update_date: Date | string | null;
	last_update_type: string | null;
	days_since_last_update: number | null;
	days_until_deadline: number | null;
	name: string;
}

// ----------------------------------------------------- INTERVIEW -----------------------------------------------------

export interface InterviewDataTransform {
	date: Date | string;
	type: string;
	location_id: number | null;
	job_id: number;
	interviewers: number[];
	note: string | null;
	attendance_type: string | null;
}

export interface InterviewData extends OwnedOut {
	date: Date | string;
	type: string;
	location_id: number | null;
	job_id: number;
	interviewers: number[];
	note: string | null;
	attendance_type: string | null;
}

export interface EnrichedInterviewData extends InterviewData {
	number: number;
}

// -------------------------------------------------------- USER -------------------------------------------------------

export interface UserDataTransform {
	email: string;
	theme?: string;
	is_admin: boolean;
	password: string;
	is_active: boolean;
	toast_active: boolean;
}

export interface UserData extends OwnedOut {
	email: string;
	is_admin: boolean;
	is_active: boolean;
	is_demo: boolean;
	toast_active: boolean;
	theme: string;
	last_login: Date | string | null;
	chase_threshold: number;
	deadline_threshold: number;
	update_limit: number;
	default_currency: string;
	pending_email: string | null;
	email_change_token: string | null;
}

// ---------------------------------------------------- SCRAPED JOB ----------------------------------------------------

export interface ScrapedJobData extends OwnedOut {
	external_job_id: string;
	is_scraped: boolean;
	is_failed: boolean;
	scrape_error: string;
	scrape_datetime: Date | string;
	is_active: boolean;
	is_imported: boolean;
	title: string | null;
	description: string | null;
	salary_min: number | null;
	salary_max: number | null;
	salary_currency: string | null;
	platform: string | null;
	url: string | null;
	deadline: Date | string | null;
	company: string | null;
	location_postcode: string | null;
	location_city: string | null;
	location_country: string | null;
	attendance_type: string | null;
	location: string | null;
	emails: number[];
}

export interface JobRating extends BaseOut {
	overall_score: number | null;
	technical_score: number | null;
	experience_score: number | null;
	educational_score: number | null;
	interest_score: number | null;
	feedback: string | null;
	script_version: number | null;
	is_success: boolean | null;
	error: string | null;
	scraped_job_id: number | null;
	user_qualification_id: number | null;
}

// ---------------------------------------------------- SERVICE LOGS ---------------------------------------------------

export interface ServiceLog extends BaseOut {
	run_datetime: string;
	run_duration: number | null;
	is_success: boolean | null;
	error_message: string | null;
}

export interface JobScraperServiceLog extends ServiceLog {
	user_found_ids: number[];
	user_processed_ids: number[];
	emails: number[];
	scraped_jobs: ScrapedJobData[];
	platform_stats: PlatformStat[];
	errors: ServiceError[];
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

export interface JobRatingServiceLog extends ServiceLog {
	rated_job_found_ids: number[];
	rated_job_succeeded_ids: number[];
	rated_job_failed_ids: number[];
	rated_job_skipped_ids: number[];
}

export interface PlatformStat {
	id: number;
	name: string;
	email_saved_ids: number[];
	email_skipped_ids: number[];
	job_found_ids: number[];
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

// ------------------------------------------------ USER QUALIFICATIONS ------------------------------------------------

export interface UserQualification extends OwnedOut {
	experience: string | null;
	skills: string | null;
	qualities: string | null;
	education: string | null;
}

export interface UserQualificationDataTransform {
	id: number | null;
	experience: string;
	skills: string;
	qualities: string;
	education: string;
	modified_at: null | Date | string;
	created_at: null | Date | string;
}
