import { renderFunctions } from "./Renders";

export const viewFields = {
	// ------------------------------------------------- GENERAL NAMES -------------------------------------------------

	name: {
		key: "name",
		label: "Name",
		type: "text",
		render: (x) => renderFunctions.name(x, true),
	},

	title: {
		key: "title",
		label: "Title",
		type: "text",
		render: (x) => renderFunctions.title(x, true),
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

	// ---------------------------------------------------- PERSONS ----------------------------------------------------

	persons: {
		key: "person",
		label: "Contacts",
		type: "text",
		render: (x) => renderFunctions.persons(x, true),
	},

	personName: {
		key: "full_name",
		label: "Full Name",
		type: "text",
		render: (x) => renderFunctions.name(x, true),
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

	status: {
		key: "status",
		label: "Status",
		type: "select",
	},

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
};
