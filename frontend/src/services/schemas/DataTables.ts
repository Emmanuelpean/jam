import { GeoLocationData, OwnedOut } from "./Base";

// -------------------------------------------------------- FILE --------------------------------------------------------

export interface FileData extends OwnedOut {
	filename: string;
	type: string;
	size: number;
	file_type: string | null;
}

export interface FileWithContentData extends FileData {
	content: string;
}

export interface FileCreate {
	filename: string;
	type: string;
	size: number;
	content: string;
	file_type?: string | null;
	is_tour?: boolean;
}

// ------------------------------------------------------- KEYWORD ------------------------------------------------------

export interface KeywordDataTransform {
	name: string;
}

export interface KeywordData extends OwnedOut {
	name: string;
}

export interface KeywordCreate {
	name: string;
	is_tour?: boolean;
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

export interface AggregatorCreate {
	name: string;
	url?: string | null;
	is_tour?: boolean;
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

export interface CompanyCreate {
	name: string;
	url?: string | null;
	description?: string | null;
	is_tour?: boolean;
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
	is_recruiter: boolean;
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
	is_recruiter: boolean;
}

export interface PersonCreate {
	first_name: string;
	last_name: string;
	email?: string | null;
	phone?: string | null;
	role?: string | null;
	linkedin_url?: string | null;
	company_id?: number | null;
	is_recruiter?: boolean;
	is_tour?: boolean;
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

export interface JobApplicationUpdateCreate {
	date: string;
	type: string;
	job_id: number;
	note?: string | null;
	is_tour?: boolean;
}

export interface EnrichedJobApplicationUpdateData extends JobApplicationUpdateData {
	number: number;
}

// -------------------------------------------------------- JOB --------------------------------------------------------

export interface JobDataTransform {
	title: string;
	is_favourite: boolean;
	description: string | null;
	note: string | null;
	url: string | null;
	salary_min: number | null;
	salary_max: number | null;
	salary_currency: string | null;
	personal_rating: number | null;
	deadline: Date | null;
	company_id: number | null;
	source_aggregator_id: number | null;
	source_type: string | null;
	recruiter_id: number | null;
	recruitment_company_id: number | null;
	location: string | null;
	application_date: Date | null;
	application_status: string | null;
	applied_via: string | null;
	application_note: string | null;
	application_aggregator_id: number | null;
	application_url: string | null;
	attendance_type: string | null;
	scraped_job_id?: number | null;
	cv_id: number | null;
	cover_letter_id: number | null;
	keywords: number[];
	contacts: number[];
}

export interface JobData extends OwnedOut {
	title: string;
	is_favourite: boolean;
	name: string;
	description: string | null;
	note: string | null;
	url: string | null;
	salary_min: number | null;
	salary_max: number | null;
	salary_currency: string | null;
	personal_rating: number | null;
	deadline: Date | null;
	company_id: number | null;
	source_aggregator_id: number | null;
	source_type: string | null;
	location: string | null;
	geolocation: GeoLocationData | null;
	recruiter_id: number | null;
	recruitment_company_id: number | null;
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
	scraped_job_id: number | null;
	cv_id: number | null;
	cover_letter_id: number | null;
	has_application: boolean;
	has_active_application: boolean;
	has_open_application: boolean;
}

export interface JobCreate {
	title: string;
	is_favourite?: boolean;
	description?: string | null;
	note?: string | null;
	url?: string | null;
	salary_min?: number | null;
	salary_max?: number | null;
	salary_currency?: string | null;
	personal_rating?: number | null;
	deadline?: string | null;
	company_id?: number | null;
	source_aggregator_id?: number | null;
	source_type?: string | null;
	location?: string | null;
	recruiter_id?: number | null;
	recruitment_company_id?: number | null;
	application_date?: string | null;
	application_status?: string | null;
	applied_via?: string | null;
	application_note?: string | null;
	application_aggregator_id?: number | null;
	application_url?: string | null;
	attendance_type?: string | null;
	keywords?: number[];
	contacts?: number[];
	scraped_job_id?: number | null;
	cv_id?: number | null;
	cover_letter_id?: number | null;
	is_tour?: boolean;
}

export interface EnrichedJobData extends JobData {
	last_update_date: Date | null;
	last_update_type: string | null;
	days_since_last_update: number | null;
	days_until_deadline: number | null;
	name: string;
}

// ----------------------------------------------------- INTERVIEW -----------------------------------------------------

export interface InterviewDataTransform {
	date: Date;
	type: string;
	location: string | null;
	job_id: number;
	interviewers: number[];
	note: string | null;
	attendance_type: string | null;
}

export interface InterviewData extends OwnedOut {
	date: Date;
	type: string;
	location: string | null;
	geolocation: GeoLocationData | null;
	job_id: number;
	interviewers: number[];
	note: string | null;
	attendance_type: string | null;
}

export interface InterviewCreate {
	date: string;
	type: string;
	job_id: number;
	location?: string | null;
	interviewers?: number[];
	note?: string | null;
	attendance_type?: string | null;
	is_tour?: boolean;
}

export interface EnrichedInterviewData extends InterviewData {
	number: number;
}

// ---------------------------------------------- SPECULATIVE APPLICATION ----------------------------------------------

export interface SpeculativeApplicationDataTransform {
	date: Date | null;
	note: string | null;
	contact_email: string | null;
	contacts: number[];
	company_id: number;
}

export interface SpeculativeApplicationData extends OwnedOut {
	date: Date | null;
	note: string | null;
	contact_email: string | null;
	contacts: number[];
	company_id: number;
}

export interface SpeculativeApplicationCreate {
	company_id: number;
	date?: string | null;
	note?: string | null;
	contact_email?: string | null;
	contacts?: number[];
	is_tour?: boolean;
}
