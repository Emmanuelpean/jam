import { renderFunctions, accessorFunctions } from "../Renders";

// Reusable column definitions that can be used across different tables
export const columns = {
	// ------------------------------------------------- GENERAL NAMES -------------------------------------------------

	// Simple name column
	name: {
		key: "name",
		label: "name",
		sortable: true,
		searchable: true,
		type: "text",
		render: (item) => renderFunctions.strongText(item, "name"),
	},

	// Simple title column
	title: {
		key: "title",
		label: "Job Title",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.jobTitle,
	},

	// Description column
	description: {
		key: "description",
		label: "Description",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.description,
	},

	// URL/Website column
	url: {
		key: "url",
		label: "Website",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.websiteUrl,
	},

	// Created date column - common across all entities
	createdAt: {
		key: "created_at",
		label: "Date Added",
		type: "date",
		sortable: true,
		searchable: false,
		render: renderFunctions.createdDate,
	},

	// ---------------------------------------------------- LOCATION ---------------------------------------------------

	// Location column with built-in modal handling
	location: {
		key: "location",
		label: "Location",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "location.name",
		searchFields: ["location.name"],
		accessor: accessorFunctions.locationName,
		render: renderFunctions.locationBadge,
	},

	// City column for location table
	city: {
		key: "city",
		label: "City",
		sortable: true,
		searchable: true,
		type: "text",
	},

	// Postcode column for location table
	postcode: {
		key: "postcode",
		label: "Postcode",
		sortable: true,
		searchable: true,
		type: "text",
	},

	// Country column for location table
	country: {
		key: "country",
		label: "Country",
		sortable: true,
		searchable: true,
		type: "text",
	},

	// --------------------------------------------------- COMPANIES ---------------------------------------------------

	// Company column with built-in modal handling
	company: {
		key: "company",
		label: "Company",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "company.name",
		searchFields: ["company.name"],
		accessor: accessorFunctions.companyName,
		render: renderFunctions.companyBadge,
	},

	// ---------------------------------------------------- PERSONS ----------------------------------------------------

	// Person full name column
	personName: {
		key: "name",
		label: "name",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "last_name",
		accessor: accessorFunctions.personName,
		render: renderFunctions.personName,
	},

	// Email column
	email: {
		key: "email",
		label: "Email",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.email,
	},

	// Phone column
	phone: {
		key: "phone",
		label: "Phone",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.phone,
	},

	// LinkedIn URL column - for people
	linkedinUrl: {
		key: "linkedin_url",
		label: "LinkedIn",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.linkedinUrl,
	},

	// ------------------------------------------------------ JOBS -----------------------------------------------------

	// Salary range column - for jobs
	salaryRange: {
		key: "salary_range",
		label: "Salary",
		sortable: true,
		searchable: false,
		type: "text",
		sortField: "salary_min",
		accessor: accessorFunctions.salaryRange,
		render: renderFunctions.salaryRange,
	},

	// Personal rating column - for jobs
	personalRating: {
		key: "personal_rating",
		label: "Rating",
		sortable: true,
		type: "number",
		render: renderFunctions.personalRating,
	},

	// Job reference column - for applications, interviews
	jobReference: {
		key: "job_title",
		label: "Job",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "job.title",
		searchFields: ["job.title", "job.company.name"],
		accessor: accessorFunctions.jobTitle,
		render: renderFunctions.jobReference,
	},

	// Note column - for applications, interviews
	note: {
		key: "note",
		label: "Notes",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.note,
	},

	// Keywords column - can be used in Jobs
	keywords: {
		key: "keywords",
		label: "Keywords",
		sortable: false,
		searchable: true,
		type: "text",
		searchFields: ["keywords.name"],
		accessor: accessorFunctions.keywords,
		render: renderFunctions.keywords,
	},
};
