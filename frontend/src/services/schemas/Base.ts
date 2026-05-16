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

export interface Config {
	scraper_email: string;
	support_email: string;
	platform_sender_emails: Record<string, string>;
	min_password_length: number;
	app_demo_username: string;
	scrape_max_retry: number;
	max_file_size_mb: number;
	monthly_scrape_quota: number;
}

export interface Status {
	maintenance_scheduled_at: Date | null;
	test_mode: boolean;
}
