import { renderFunctions } from "./Renders";

export const viewFields = {
	// ------------------------------------------------- GENERAL NAMES -------------------------------------------------

	name: {
		key: "name",
		label: "Name",
		type: "text",
	},

	title: {
		key: "title",
		label: "Title",
		type: "text",
	},

	description: {
		key: "description",
		label: "Description",
		type: "textarea",
		render: (x) => renderFunctions.description(x, true),
	},

	url: {
		key: "url",
		label: "Website",
		type: "url",
		render: (x) => renderFunctions.url(x, true),
	},

	createdAt: {
		key: "created_at",
		label: "Date Added",
		type: "date",
		render: (x) => renderFunctions.createdDate(x, true),
	},

	modifiedAt: {
		key: "modified_at",
		label: "Modified On",
		type: "date",
		render: (x) => renderFunctions.modifiedDate(x, true),
	},

	note: {
		key: "note",
		label: "Notes",
		type: "textarea",
		render: (x) => renderFunctions.note(x, true),
	},

	date: {
		key: "date",
		label: "Date",
		type: "date",
		render: (x) => renderFunctions.date(x, true),
	},

	type: {
		key: "type",
		label: "Type",
		type: "text"
	},

	// ---------------------------------------------------- LOCATION ---------------------------------------------------

	location: {
		key: "location",
		label: "Location",
		type: "text",
		render: (x) => renderFunctions.location(x, true),
	},

	city: {
		key: "city",
		label: "City",
		type: "text",
	},

	postcode: {
		key: "postcode",
		label: "Postcode",
		type: "text",
	},

	country: {
		key: "country",
		label: "Country",
		type: "text",
	},

	// --------------------------------------------------- COMPANIES ---------------------------------------------------

	company: {
		key: "company",
		label: "Company",
		type: "text",
		render: (x) => renderFunctions.company(x, true),
	},

	// ---------------------------------------------------- KEYWORDS ---------------------------------------------------

	keywords: {
		key: "keywords",
		label: "Tags",
		type: "text",
		render: (x) => renderFunctions.keywords(x, true),
	},

	// ---------------------------------------------------- PERSONS ----------------------------------------------------

	persons: {
		key: "person",
		label: "Contacts",
		type: "text",
		render: (x) => renderFunctions.contacts(x, true),
	},

	personName: {
		key: "name",
		label: "Full Name",
		type: "text",
	},

	email: {
		key: "email",
		label: "Email",
		type: "email",
		render: (x) => renderFunctions.email(x, true),
	},

	phone: {
		key: "phone",
		label: "Phone",
		type: "text",
		render: (x) => renderFunctions.phone(x, true),
	},

	linkedinUrl: {
		key: "linkedin_url",
		label: "LinkedIn Profile",
		type: "url",
		render: (x) => renderFunctions.linkedinUrl(x, true),
	},

	// ------------------------------------------------------ JOBS -----------------------------------------------------

	salaryRange: {
		key: "salary_range",
		label: "Salary Range",
		type: "text",
		render: (x) => renderFunctions.salaryRange(x, true),
	},

	personalRating: {
		key: "personal_rating",
		label: "Personal Rating",
		type: "text",
		render: (x) => renderFunctions.personalRating(x, true),
	},

	jobApplication: {
		key: "job_application",
		label: "Application Status",
		type: "text",
		render: (x) => renderFunctions.jobApplication(x, true),
	}
};
