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

// ------------------------------------------------------ SETTING ------------------------------------------------------

export interface UserDataAccountUpdate {
	email: string | null;
	password: string | null;
	current_password: string | null;
	first_name: string | null;
	last_name: string | null;
}

export interface UserDataPreferences {
	theme: string;
	chase_threshold: number;
	deadline_threshold: number;
	update_limit: number;
	default_currency: string;
}

export type UserDataPreferencesUpdate = Partial<UserDataPreferences>;

export interface UserDataPremium {
	is_active: boolean;
	job_scraping_active: boolean;
	job_rating_active: boolean;
}

export interface UserDataPremiumUpdate {
	job_scraping_active: boolean | null;
	job_rating_active: boolean | null;
}

export interface UserDataTransform {
	email: string;
	is_admin: boolean;
	password: string;
	is_active: boolean;
}

export interface UserData extends OwnedOut {
	email: string;
	is_admin: boolean;
	is_active: boolean;
	is_demo: boolean;
	last_login: Date | string | null;
	first_name: string | null;
	last_name: string | null;
	name: string | null;
	premium: UserDataPremium;
	preferences: UserDataPreferences;
}

// ------------------------------------------------ USER QUALIFICATIONS ------------------------------------------------

export interface UserQualification extends OwnedOut {
	experience: string | null;
	skills: string | null;
	qualities: string | null;
	education: string | null;
	interests: string | null;
}
