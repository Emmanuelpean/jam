
import { renderFunctions } from "./Renders";

export const viewFields = {
	// ------------------------------------------------- GENERAL NAMES -------------------------------------------------

	name: (overrides = {}) => ({
		key: "name",
		label: "Name",
		type: "text",
		...overrides,
	}),

	title: (overrides = {}) => ({
		key: "title",
		label: "Title",
		type: "text",
		...overrides,
	}),

	description: (overrides = {}) => ({
		key: "description",
		label: "Description",
		type: "textarea",
		render: (x) => renderFunctions.description(x, true),
		...overrides,
	}),

	url: (overrides = {}) => ({
		key: "url",
		label: "Website",
		type: "url",
		render: (x) => renderFunctions.url(x, true),
		...overrides,
	}),

	createdAt: (overrides = {}) => ({
		key: "created_at",
		label: "Date Added",
		type: "date",
		render: (x) => renderFunctions.createdDate(x, true),
		...overrides,
	}),

	modifiedAt: (overrides = {}) => ({
		key: "modified_at",
		label: "Modified On",
		type: "date",
		render: (x) => renderFunctions.modifiedDate(x, true),
		...overrides,
	}),

	note: (overrides = {}) => ({
		key: "note",
		label: "Notes",
		type: "textarea",
		render: (x) => renderFunctions.note(x, true),
		...overrides,
	}),

	date: (overrides = {}) => ({
		key: "date",
		label: "Date",
		type: "date",
		render: (x) => renderFunctions.date(x, true),
		...overrides,
	}),

	type: (overrides = {}) => ({
		key: "type",
		label: "Type",
		type: "text",
		...overrides,
	}),

	// ---------------------------------------------------- LOCATION ---------------------------------------------------

	location: (overrides = {}) => ({
		key: "location",
		label: "Location",
		type: "text",
		render: (x) => renderFunctions.location(x, true),
		...overrides,
	}),

	city: (overrides = {}) => ({
		key: "city",
		label: "City",
		type: "text",
		...overrides,
	}),

	postcode: (overrides = {}) => ({
		key: "postcode",
		label: "Postcode",
		type: "text",
		...overrides,
	}),

	country: (overrides = {}) => ({
		key: "country",
		label: "Country",
		type: "text",
		...overrides,
	}),

	// --------------------------------------------------- COMPANIES ---------------------------------------------------

	company: (overrides = {}) => ({
		key: "company",
		label: "Company",
		type: "text",
		render: (x) => renderFunctions.company(x, true),
		...overrides,
	}),

	// ---------------------------------------------------- KEYWORDS ---------------------------------------------------

	keywords: (overrides = {}) => ({
		key: "keywords",
		label: "Tags",
		type: "text",
		render: (x) => renderFunctions.keywords(x, true),
		...overrides,
	}),

	// ---------------------------------------------------- PERSONS ----------------------------------------------------

	persons: (overrides = {}) => ({
		key: "person",
		label: "Contacts",
		type: "text",
		render: (x) => renderFunctions.contacts(x, true),
		...overrides,
	}),

	personName: (overrides = {}) => ({
		key: "name",
		label: "Full Name",
		type: "text",
		...overrides,
	}),

	email: (overrides = {}) => ({
		key: "email",
		label: "Email",
		type: "email",
		render: (x) => renderFunctions.email(x, true),
		...overrides,
	}),

	phone: (overrides = {}) => ({
		key: "phone",
		label: "Phone",
		type: "text",
		render: (x) => renderFunctions.phone(x, true),
		...overrides,
	}),

	linkedinUrl: (overrides = {}) => ({
		key: "linkedin_url",
		label: "LinkedIn Profile",
		type: "url",
		render: (x) => renderFunctions.linkedinUrl(x, true),
		...overrides,
	}),

	// ------------------------------------------------------ JOBS -----------------------------------------------------

	salaryRange: (overrides = {}) => ({
		key: "salary_range",
		label: "Salary Range",
		type: "text",
		render: (x) => renderFunctions.salaryRange(x, true),
		...overrides,
	}),

	personalRating: (overrides = {}) => ({
		key: "personal_rating",
		label: "Personal Rating",
		type: "text",
		render: (x) => renderFunctions.personalRating(x, true),
		...overrides,
	}),

	jobApplication: (overrides = {}) => ({
		key: "job_application",
		label: "Application Status",
		type: "text",
		render: (x) => renderFunctions.jobApplication(x, true),
		...overrides,
	}),

	status: (overrides = {}) => ({
		key: "status",
		label: "Status",
		type: "text",
		render: (x) => renderFunctions.status(x, true),
		...overrides,
	}),

	interviewers: (overrides = {}) => ({
		key: "person",
		label: "Interviewers",
		type: "text",
		render: (x) => renderFunctions.contacts(x, true, "interviewers"),
		...overrides,
	}),

	job: (overrides = {}) => ({
		key: "job",
		label: "Job",
		type: "text",
		render: (x) => renderFunctions.job(x, true),
		...overrides,
	}),

	aggregator: (overrides = {}) => ({
		key: "aggregator",
		label: "Aggregator",
		type: "text",
		render: (x) => renderFunctions.aggregator(x, true),
		...overrides,
	}),

	appliedVia: (overrides = {}) => ({
		key: "applied_via",
		label: "Applied Via",
		type: "text",
		...overrides,
	}),

	cv: (overrides = {}) => ({
		key: "cv",
		label: "CV",
		type: "file",
		render: (x) => renderFunctions.cv(x, true),
		...overrides,
	}),

	coverLetter: (overrides = {}) => ({
		key: "cover_letter",
		label: "Cover Letter",
		type: "file",
		render: (x) => renderFunctions.coverLetter(x, true),
		...overrides,
	}),

	files: (overrides = {}) => ({
		key: "files",
		label: "Files",
		type: "file",
		render: (x) => renderFunctions.files(x, true),
		...overrides,
	})

};