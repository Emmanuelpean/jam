interface BaseOut {
	id: number;
	created_at: string;
	modified_at: string;
}

interface OwnedOut extends BaseOut {
	owner_id: number;
}

// ------------------------------------------------------- COMPANY ------------------------------------------------------

export interface CompanyCreate {
	name: string;
	description?: string;
	url?: string;
}

export interface CompanyOut extends CompanyCreate, OwnedOut {}

// ------------------------------------------------------- KEYWORD ------------------------------------------------------

export interface KeywordCreate {
	name: string;
}

export interface KeywordOut extends KeywordCreate, OwnedOut {}

// ----------------------------------------------------- AGGREGATOR -----------------------------------------------------

export interface AggregatorCreate {
	name: string;
	url?: string;
}

export interface AggregatorOut extends AggregatorCreate, OwnedOut {}

// ------------------------------------------------------- PERSON -------------------------------------------------------

export interface PersonCreate {
	first_name: string;
	last_name: string;
	email?: string;
	phone?: string;
	linkedin_url?: string;
	role?: string;
	company_id?: number;
}

export interface PersonOut extends PersonCreate, OwnedOut {
	company?: CompanyOut;
	name?: string;
}

// --------------------------------------------------------- JOB --------------------------------------------------------

export interface SettingData {
	name: string;
	value: string;
	description?: string;
	isActive: boolean;
}

export interface AggregatorData {
	id?: number;
	name: string;
	url: string;
}

export interface KeywordData {
	id?: number;
	name: string;
}

export interface PersonData {
	first_name: string;
	last_name: string;
	email?: string;
	phone?: string;
	role?: string;
	linkedin_url?: string;
	company_id?: number | null;
}

export interface InterviewData {
	date?: string;
	type?: string;
	location_id?: string | number;
	job_id?: string | number;
	interviewers?: any[];
	note?: string;
	attendance_type?: string;
	job?: JobData;
}

export interface LocationData extends OwnedOut {
	city?: string | null;
	postcode?: string | null;
	country?: string | null;
	name: string;
}

export interface JobData {
	id?: number;
	name?: string;
	title: string;
	description?: string | null;
	note?: string | null;
	url?: string | null;
	salary_min?: number | null;
	salary_max?: number | null;
	personal_rating?: number | null;
	deadline?: Date | null;
	company_id?: number | null;
	location_id?: number | null;
	application_date?: Date | null;
	application_status?: string | null;
	applied_via?: string | null;
	application_note?: string | null;
	application_aggregator_id?: number | null;
	application_url?: string | null;
	attendance_type?: string | null;
	keywords?: KeywordData[] | number[];
	contacts?: AggregatorData[] | number[];
}

export interface ApplicationData {
	id?: number;
	date: string;
	url?: string | null;
	status: string;
	job_id?: number;
	applied_via: string;
	aggregator_id?: number | null;
	note?: string | null;
}

export interface UserData {
	id?: number;
	email: string;
	is_admin?: boolean;
	theme?: string;
	last_login?: string;
	created_at?: string;
}

export interface CompanyData {
	name: string;
	url?: string | null;
	description?: string | null;
}

export interface JobApplicationUpdateData {
	date: string;
	type: string;
	job_id?: string | number;
	note?: string;
	id?: string | number;
}
