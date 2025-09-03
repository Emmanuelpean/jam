import { ReactNode } from "react";
import { renderFunctions, RenderParams } from "./ViewRenders";

interface ViewFieldOverrides {
	key?: string;
	label?: string;
	type?: string;
	columnClass?: string;
	outsideCard?: boolean;
	render?: (params: RenderParams) => ReactNode;
}

interface ViewField {
	key: string;
	label: string;
	type?: string;
	columnClass?: string;
	outsideCard?: boolean;
	render?: (params: RenderParams) => ReactNode;
}

type ViewFieldFactory = (overrides?: ViewFieldOverrides) => ViewField;

interface ViewFields {
	[key: string]: ViewFieldFactory;
}

export const viewFields: ViewFields = {
	// ------------------------------------------------- GENERAL NAMES -------------------------------------------------

	name: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "name",
		label: "Name",
		...overrides,
	}),

	title: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "title",
		label: "Title",
		...overrides,
	}),

	description: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "description",
		label: "Description",
		render: (params: RenderParams) => renderFunctions.description({ ...params, view: true }),
		...overrides,
	}),

	url: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "url",
		label: "Website",
		render: (params: RenderParams) => renderFunctions.url({ ...params, view: true }),
		...overrides,
	}),

	note: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "note",
		label: "Notes",
		render: (params: RenderParams) => renderFunctions.note({ ...params, view: true }),
		...overrides,
	}),

	date: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "date",
		label: "Date",
		render: (params: RenderParams) => renderFunctions.date({ ...params, view: true }),
		...overrides,
	}),

	datetime: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "date",
		label: "Date & Time",
		render: (params: RenderParams) => renderFunctions.datetime({ ...params, view: true }),
		...overrides,
	}),

	type: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "type",
		label: "Type",
		...overrides,
	}),

	// ------------------------------------------------------ USER -----------------------------------------------------

	appTheme: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "theme",
		label: "Theme",
		render: renderFunctions.appTheme,
		...overrides,
	}),

	isAdmin: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "is_admin",
		label: "Admin",
		render: (params: RenderParams) => renderFunctions.isAdmin({ ...params, view: true }),
		...overrides,
	}),

	// ---------------------------------------------------- LOCATION ---------------------------------------------------

	location: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "location",
		label: "Location",
		render: (params: RenderParams) => renderFunctions.location({ ...params, view: true }),
		...overrides,
	}),

	city: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "city",
		label: "City",
		...overrides,
	}),

	postcode: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "postcode",
		label: "Postcode",
		...overrides,
	}),

	country: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "country",
		label: "Country",
		...overrides,
	}),

	locationMap: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "location_map",
		label: "📍 Location on Map",
		type: "custom",
		columnClass: "col-12",
		render: renderFunctions.locationMap,
		...overrides,
	}),

	// --------------------------------------------------- COMPANIES ---------------------------------------------------

	company: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "company",
		label: "Company",
		render: renderFunctions.company,
		...overrides,
	}),

	// ---------------------------------------------------- KEYWORDS ---------------------------------------------------

	keywords: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "keywords",
		label: "Tags",
		render: (params: RenderParams) => renderFunctions.keywords({ ...params, view: true }),
		...overrides,
	}),

	// ---------------------------------------------------- PERSONS ----------------------------------------------------

	persons: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "person",
		label: "Contacts",
		render: (params: RenderParams) => renderFunctions.contacts({ ...params, view: true }),
		...overrides,
	}),

	personName: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "name",
		label: "Full Name",
		...overrides,
	}),

	email: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "email",
		label: "Email",
		render: (params: RenderParams) => renderFunctions.email({ ...params, view: true }),
		...overrides,
	}),

	phone: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "phone",
		label: "Phone",
		render: (params: RenderParams) => renderFunctions.phone({ ...params, view: true }),
		...overrides,
	}),

	linkedinUrl: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "linkedin_url",
		label: "LinkedIn Profile",
		render: (params: RenderParams) => renderFunctions.linkedinUrl({ ...params, view: true }),
		...overrides,
	}),

	role: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "role",
		label: "Role",
		...overrides,
	}),

	// ------------------------------------------------------ JOBS -----------------------------------------------------

	salaryRange: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "salary_range",
		label: "Salary Range",
		render: (params: RenderParams) => renderFunctions.salaryRange({ ...params, view: true }),
		...overrides,
	}),

	personalRating: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "personal_rating",
		label: "Personal Rating",
		render: (params: RenderParams) => renderFunctions.personalRating({ ...params, view: true }),
		...overrides,
	}),

	job: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "job",
		label: "Job",
		render: (params: RenderParams) => renderFunctions.job({ ...params, view: true }),
		...overrides,
	}),

	// ------------------------------------------------ JOB APPLICATION ------------------------------------------------

	jobApplication: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "job_application",
		label: "Application Status",
		render: (params: RenderParams) => renderFunctions.jobApplication({ ...params, view: true }),
		...overrides,
	}),

	status: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "status",
		label: "Status",
		render: (params: RenderParams) => renderFunctions.status({ ...params, view: true }),
		...overrides,
	}),

	interviewers: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "person",
		label: "Interviewers",
		render: (params: RenderParams) => renderFunctions.interviewers({ ...params, view: true }),
		...overrides,
	}),

	appliedVia: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "applied_via",
		label: "Applied Via",
		render: (params: RenderParams) => renderFunctions.appliedVia({ ...params, view: true }),
		...overrides,
	}),

	// --------------------------------------------------- INTERVIEW ---------------------------------------------------

	interviews: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "interviews",
		label: "Interviews",
		render: renderFunctions.interviewTable,
		...overrides,
	}),

	// --------------------------------------------- JOB APPLICATION UPDATE --------------------------------------------

	updates: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "updates",
		label: "Updates",
		render: renderFunctions.jobApplicationUpdateTable,
		...overrides,
	}),

	updateType: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "type",
		label: "Type",
		render: renderFunctions.updateType,
		...overrides,
	}),

	jobs: (overrides: ViewFieldOverrides = {}): ViewField => ({
		key: "job",
		label: "Jobs",
		render: renderFunctions.jobTable,
		outsideCard: true,
		...overrides,
	}),
};
