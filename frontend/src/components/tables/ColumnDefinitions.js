import { renderFunctions, accessorFunctions } from "../Renders";

export const columns = {
	// ------------------------------------------------- GENERAL NAMES -------------------------------------------------

	name: {
		key: "name",
		label: "Name",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.name,
	},

	title: {
		key: "title",
		label: "Title",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.title,
	},

	description: {
		key: "description",
		label: "Description",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.description,
	},

	url: {
		key: "url",
		label: "Website",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.url,
	},

	createdAt: {
		key: "created_at",
		label: "Date Added",
		type: "date",
		sortable: true,
		searchable: true,
		render: renderFunctions.createdDate,
	},

	modifiedAt: {
		key: "modified_at",
		label: "Modified On",
		type: "date",
		sortable: true,
		searchable: true,
		render: renderFunctions.createdDate,
	},

	note: {
		key: "note",
		label: "Notes",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.note,
	},

	// ---------------------------------------------------- LOCATION ---------------------------------------------------

	location: {
		key: "location",
		label: "Location",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "location.name",
		searchFields: ["location.name"],
		render: renderFunctions.location,
	},

	city: {
		key: "city",
		label: "City",
		sortable: true,
		searchable: true,
		type: "text",
	},

	postcode: {
		key: "postcode",
		label: "Postcode",
		sortable: true,
		searchable: true,
		type: "text",
	},

	country: {
		key: "country",
		label: "Country",
		sortable: true,
		searchable: true,
		type: "text",
	},

	// --------------------------------------------------- COMPANIES ---------------------------------------------------

	company: {
		key: "company",
		label: "Company",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "company.name",
		searchFields: ["company.name"],
		accessor: accessorFunctions.companyName,
		render: renderFunctions.company,
	},

	// ---------------------------------------------------- PERSONS ----------------------------------------------------

	personName: {
		key: "name",
		label: "name",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "last_name",
		accessor: accessorFunctions.personName,
		render: renderFunctions.name,
	},

	email: {
		key: "email",
		label: "Email",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.email,
	},

	phone: {
		key: "phone",
		label: "Phone",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.phone,
	},

	linkedinUrl: {
		key: "linkedin_url",
		label: "LinkedIn",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.linkedinUrl,
	},

	// ------------------------------------------------------ JOBS -----------------------------------------------------

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

	personalRating: {
		key: "personal_rating",
		label: "Rating",
		sortable: true,
		type: "number",
		render: renderFunctions.personalRating,
	},

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
