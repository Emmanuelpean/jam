export interface BaseOut {
	id: number;
	created_at: Date;
	modified_at: Date;
}

export interface OwnedOut extends BaseOut {
	owner_id: number;
	is_tour: boolean;
}

export interface GeoLocationData extends BaseOut {
	query: string;
	latitude: number | null;
	longitude: number | null;
	city: string | null;
	postcode: string | null;
	country: string | null;
}

export interface ColumnLimits {
	// User / auth
	email: number;
	password: number;
	first_name: number;
	last_name: number;
	// User profile
	experience: number;
	education: number;
	skills: number;
	qualities: number;
	interests: number;
	// Shared
	name: number;
	url: number;
	note: number;
	location: number;
	attendance_type: number;
	currency: number;
	description: number;
	// File
	file_name: number;
	file_mimetype: number;
	file_type: number;
	// Person
	phone: number;
	role: number;
	// Job
	job_title: number;
	application_status: number;
	applied_via: number;
	source_type: number;
	// Interview
	interview_type: number;
	// Update
	update_type: number;
}

export interface Config {
	scraper_email: string;
	support_email: string;
	platform_sender_emails: Record<string, string>;
	min_password_length: number;
	app_demo_username: string;
	scrape_max_retry: number;
	max_file_size_mb: number;
	monthly_scrape_quota: number;
	column_limits: ColumnLimits;
}

export interface Status {
	maintenance_scheduled_at: Date | null;
	test_mode: boolean;
}
