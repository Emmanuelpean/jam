import { BaseOut, GeoLocation, OwnedOut } from "./Base";

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
	geolocation: GeoLocation | null;
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

// ---------------------------------------------- SPECULATIVE APPLICATION ----------------------------------------------

export interface SpeculativeApplicationDataTransform {
	date: Date | string | null;
	note: string | null;
	contact_email: string | null;
	contacts: number[];
	company_id: number;
}

export interface SpeculativeApplicationData extends OwnedOut {
	date: Date | string | null;
	note: string | null;
	contact_email: string | null;
	contacts: number[];
	company_id: number;
}
