import { BaseOut, OwnedOut } from "./Base";

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

// -------------------------------------------------- USER PREFERENCES -------------------------------------------------

export interface UserPreferences {
	theme: string;
	dark_mode: boolean;
	chase_threshold: number;
	deadline_threshold: number;
	update_limit: number;
	default_currency: string;
}

export type UserPreferencesUpdate = Partial<UserPreferences>;

// -------------------------------------------------- PREMIUM DETAILS --------------------------------------------------

export interface PremiumDetails {
	is_active: boolean;
	job_scraping_active: boolean;
	job_rating_active: boolean;
}

export interface PremiumDetailsUpdate {
	job_scraping_active?: boolean | null;
	job_rating_active?: boolean | null;
}

// --------------------------------------------------- STRIPE DETAILS --------------------------------------------------

export interface StripeDetails {
	subscription_status: string | null;
	trial_end_date: number | null;
}

// ----------------------------------------------------- USER DATA -----------------------------------------------------

export interface UserDataTransform {
	email: string;
	is_admin: boolean;
	password: string;
	is_active: boolean;
	premium: PremiumDetails;
}

export interface UserDataUpdate {
	email?: string | null;
	password?: string | null;
	current_password?: string | null;
	first_name?: string | null;
	last_name?: string | null;
	app_version?: string | null;
	premium?: PremiumDetailsUpdate | null;
	preferences?: UserPreferencesUpdate | null;
}

export interface UserData extends OwnedOut {
	email: string;
	is_admin: boolean;
	is_active: boolean;
	is_demo: boolean;
	last_login: Date | string | null;
	app_version: string | null;
	first_name: string | null;
	last_name: string | null;
	name: string | null;
	pending_email_change: string | null;
	premium: PremiumDetails;
	preferences: UserPreferences;
	stripe_details: StripeDetails;
}

// ------------------------------------------------ USER QUALIFICATIONS ------------------------------------------------

export interface UserQualification extends OwnedOut {
	experience: string | null;
	skills: string | null;
	qualities: string | null;
	education: string | null;
	interests: string | null;
}
