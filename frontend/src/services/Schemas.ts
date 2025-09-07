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

// ------------------------------------------------------ LOCATION ------------------------------------------------------

export interface LocationCreate extends BaseOut {
	postcode?: string;
	city?: string;
	country?: string;
}

export interface LocationOut extends LocationCreate, OwnedOut {
	name?: string;
}

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

export interface AggregatorData {
	id?: number;
	name: string;
	url: string;
}

export interface KeywordData {
	id?: number;
	name: string;
}

export interface JobData {
	id?: number;
	title: string;
	description?: string | null;
	note?: string | null;
	url?: string | null;
	salary_min?: number | null;
	salary_max?: number | null;
	personal_rating?: number | null;
	company_id?: number | null;
	location_id?: number | null;
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
	email: string;
	password?: string;
	theme?: string;
	is_admin?: boolean;
}

export interface CompanyData {
	name: string;
	url?: string | null;
	description?: string | null;
}
