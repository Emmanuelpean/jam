import { Theme } from "../utils/Theme";

interface BaseOut {
	id: number;
	created_at: string;
	modified_at: string;
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
	date: Date;
	type: string;
	job_id: number;
	note: string | null;
}

export interface JobApplicationUpdateData extends OwnedOut {
	date: Date;
	type: string;
	job_id: number;
	note: string | null;
}

export interface ScrapedJobUpdate {
	id?: number;
	is_imported?: boolean;
	is_active?: boolean;
}

// -------------------------------------------------------- JOB --------------------------------------------------------

export interface JobDataTransform {
	title: string;
	description: string | null;
	note: string | null;
	url: string | null;
	salary_min: number | null;
	salary_max: number | null;
	personal_rating: number | null;
	deadline: Date | null;
	company_id: number | null;
	source_id: number | null;
	location_id: number | null;
	application_date: Date | null;
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
	personal_rating: number | null;
	deadline: Date | null;
	company_id: number | null;
	source_id: number | null;
	location_id: number | null;
	followup_snooze_datetime: Date | null;
	application_date: Date | null;
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
	last_update_date: Date | null;
	last_update_type: string | null;
	days_since_last_update: number | null;
	days_until_deadline: number | null;
}

// ----------------------------------------------------- INTERVIEW -----------------------------------------------------

export interface InterviewDataTransform {
	date: Date;
	type: string;
	location_id: number | null;
	job_id: number;
	interviewers: number[];
	note: string | null;
	attendance_type: string | null;
}

export interface InterviewData extends OwnedOut {
	date: Date;
	type: string;
	location_id: number | null;
	job_id: number;
	interviewers: number[];
	note: string | null;
	attendance_type: string | null;
}

// -------------------------------------------------------- USER -------------------------------------------------------

export interface UserDataTransform {
	email: string;
	theme?: Theme;
	is_admin: boolean;
	toast_active: boolean;
}

export interface UserData extends OwnedOut {
	email: string;
	is_admin: boolean;
	toast_active: boolean;
	theme: Theme;
	last_login: string | null;
	chase_threshold: number;
	deadline_threshold: number;
	update_limit: number;
}
