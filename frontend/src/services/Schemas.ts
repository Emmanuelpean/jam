interface BaseOut {
	id: number;
	created_at: string;
	modified_at: string;
}

interface OwnedOut extends BaseOut {
	owner_id: number;
}

// -------------------------------------------------------- USER --------------------------------------------------------

export interface UserCreate {
	password: string;
	email: string;
}

export interface UserOut extends BaseOut {
	email: string;
	theme: string;
	is_admin?: boolean;
	last_login?: string;
}

export interface UserLogin {
	email: string;
	password: string;
}

export interface UserUpdate {
	current_password?: string;
	email?: string;
	theme?: string;
	password?: string;
	is_admin?: boolean;
	last_login?: string;
}

// -------------------------------------------------------- TOKEN -------------------------------------------------------

export interface Token {
	access_token: string;
	token_type: string;
}

export interface TokenData {
	id?: string;
}

// ------------------------------------------------------- COMPANY ------------------------------------------------------

export interface CompanyCreate {
	name: string;
	description?: string;
	url?: string;
}

export interface CompanyOut extends CompanyCreate, OwnedOut {}

export interface CompanyUpdate {
	name?: string;
	description?: string;
	url?: string;
}

// ------------------------------------------------------- KEYWORD ------------------------------------------------------

export interface KeywordCreate {
	name: string;
}

export interface KeywordOut extends KeywordCreate, OwnedOut {}

export interface KeywordUpdate {
	name?: string;
}

// ----------------------------------------------------- AGGREGATOR -----------------------------------------------------

export interface AggregatorCreate {
	name: string;
	url?: string;
}

export interface AggregatorOut extends AggregatorCreate, OwnedOut {}

export interface AggregatorUpdate {
	name?: string;
	url?: string;
}

// ------------------------------------------------------ LOCATION ------------------------------------------------------

export interface LocationCreate extends BaseOut {
	postcode?: string;
	city?: string;
	country?: string;
}

export interface LocationOut extends LocationCreate, OwnedOut {
	name?: string;
}

export interface LocationUpdate extends LocationCreate {}

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

export interface PersonSimple extends PersonCreate, OwnedOut {
	company?: CompanyOut;
	name?: string;
}

export interface PersonOut extends PersonCreate, OwnedOut {
	company?: CompanyOut;
	name?: string;
}

export interface PersonUpdate {
	first_name?: string;
	last_name?: string;
	email?: string;
	phone?: string;
	linkedin_url?: string;
	role?: string;
	company_id?: number;
}

// --------------------------------------------------------- JOB --------------------------------------------------------

export interface JobCreate {
	title: string;
	description?: string;
	salary_min?: number;
	salary_max?: number;
	personal_rating?: number;
	url?: string;
	company_id?: number;
	location_id?: number;
	duplicate_id?: number;
	note?: string;
	keywords: number[];
	contacts: number[];
	deadline?: string;
	attendance_type?: string;
	source_id?: number;
}

// export interface JobSimple extends JobCreate, OwnedOut {
// 	company?: CompanyOut;
// 	location?: LocationOut;
// 	keywords: KeywordOut[];
// 	contacts: PersonSimple[];
// 	name?: string;
// 	source?: AggregatorOut;
// }
//
// export interface JobOut extends JobCreate, OwnedOut {
// 	company?: CompanyOut;
// 	location?: LocationOut;
// 	keywords: KeywordOut[];
// 	job_application?: JobApplicationOut;
// 	contacts: PersonSimple[];
// 	name?: string;
// 	source?: AggregatorOut;
// }
//
// export interface JobToChaseOut extends JobOut {
// 	last_update_type: string;
// 	days_since_last_update: number;
// }

export interface JobUpdate {
	title?: string;
	description?: string;
	salary_min?: number;
	salary_max?: number;
	personal_rating?: number;
	url?: string;
	company_id?: number;
	location_id?: number;
	duplicate_id?: number;
	note?: string;
	keywords?: number[];
	contacts?: number[];
	deadline?: string;
	attendance_type?: string;
	source_id?: number;
}

// --------------------------------------------------- JOB APPLICATION --------------------------------------------------

export interface JobApplicationCreate {
	date: string;
	url?: string;
	job_id: number;
	status: string;
	note?: string;
	applied_via?: string;
	aggregator_id?: number;
	cv_id?: number;
	cover_letter_id?: number;
}
//
// export interface JobApplicationOut extends JobApplicationCreate, OwnedOut {
// 	job?: JobSimple;
// 	aggregator?: AggregatorOut;
// 	interviews: InterviewSimple[];
// 	updates: JobApplicationUpdateSimpleOut[];
// }
//
// export interface JobApplicationSimple extends JobApplicationCreate, OwnedOut {
// 	job?: JobSimple;
// 	aggregator?: AggregatorOut;
// }

export interface JobApplicationUpdate {
	date?: string;
	url?: string;
	job_id?: number;
	status?: string;
	note?: string;
	applied_via?: string;
	aggregator_id?: number;
	cv_id?: number;
	cover_letter_id?: number;
}

// ------------------------------------------------------ INTERVIEW -----------------------------------------------------

export interface InterviewCreate {
	date: string;
	location_id?: number;
	job_application_id: number;
	note?: string;
	type?: string;
	interviewers?: number[];
	attendance_type?: string;
}

// export interface InterviewSimple extends InterviewCreate, OwnedOut {
// 	location?: LocationOut;
// 	interviewers: PersonSimple[];
// }
//
// export interface InterviewOut extends InterviewCreate, OwnedOut {
// 	location?: LocationOut;
// 	interviewers: PersonSimple[];
// 	job_application?: JobApplicationSimple;
// }

export interface InterviewUpdate {
	date?: string;
	location_id?: number;
	job_application_id?: number;
	note?: string;
	type?: string;
	interviewers?: number[];
	attendance_type?: string;
}

// ----------------------------------------------- JOB APPLICATION UPDATE -----------------------------------------------

export interface JobApplicationUpdateCreate {
	date: string;
	type: string;
	job_application_id: number;
	note?: string;
}

// export interface JobApplicationUpdateOut extends JobApplicationUpdateCreate, OwnedOut {
// 	job_application?: JobApplicationSimple;
// }

export interface JobApplicationUpdateSimpleOut extends JobApplicationUpdateCreate, OwnedOut {}

export interface JobApplicationUpdateUpdate {
	date?: string;
	type?: string;
	job_application_id?: number;
	note?: string;
}
