import { useEffect, useState } from "react";
import { fetchCountries } from "../../utils/CountryUtils";

// Hook for country loading that can be used by components
export const useCountries = () => {
	const [countries, setCountries] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);

	useEffect(() => {
		const loadCountries = async () => {
			try {
				setLoading(true);
				const countriesList = await fetchCountries();
				setCountries(countriesList);
				setError(null);
			} catch (err) {
				console.error("Failed to load countries:", err);
				setError(err);
			} finally {
				setLoading(false);
			}
		};

		loadCountries();
	}, []);

	return { countries, loading, error };
};

// Common form field definitions for reuse across modals
// Each field is a function that accepts override attributes
export const formFields = {
	// ------------------------------------------------- BASIC FIELDS -------------------------------------------------

	title: (overrides = {}) => ({
		name: "title",
		label: "Title",
		type: "text",
		required: true,
		placeholder: "Enter title",
		...overrides,
	}),

	name: (overrides = {}) => ({
		name: "name",
		label: "Name",
		type: "text",
		required: true,
		placeholder: "Enter name",
		...overrides,
	}),

	description: (overrides = {}) => ({
		name: "description",
		label: "Description",
		type: "textarea",
		rows: 4,
		placeholder: "Enter description...",
		...overrides,
	}),

	note: (overrides = {}) => ({
		name: "note",
		label: "Notes",
		type: "textarea",
		rows: 3,
		placeholder: "Add your notes...",
		...overrides,
	}),

	url: (overrides = {}) => ({
		name: "url",
		label: "URL",
		type: "text",
		placeholder: "https://...",
		...overrides,
	}),

	date: (overrides = {}) => ({
		name: "date",
		label: "Date",
		type: "date",
		required: true,
		...overrides,
	}),

	datetime: (overrides = {}) => ({
		name: "date",
		label: "Date & Time",
		type: "datetime-local",
		required: true,
		placeholder: "Select date and time",
		...overrides,
	}),

	// ------------------------------------------------- PERSON FIELDS ------------------------------------------------

	firstName: (overrides = {}) => ({
		name: "first_name",
		label: "First Name",
		type: "text",
		required: true,
		placeholder: "Enter first name",
		...overrides,
	}),

	lastName: (overrides = {}) => ({
		name: "last_name",
		label: "Last Name",
		type: "text",
		required: true,
		placeholder: "Enter last name",
		...overrides,
	}),

	email: (overrides = {}) => ({
		name: "email",
		label: "Email",
		type: "email",
		required: false,
		placeholder: "person@company.com",
		...overrides,
	}),

	phone: (overrides = {}) => ({
		name: "phone",
		label: "Phone",
		type: "tel",
		required: false,
		placeholder: "+1-555-0123",
		...overrides,
	}),

	linkedinUrl: (overrides = {}) => ({
		name: "linkedin_url",
		label: "LinkedIn Profile",
		type: "text",
		required: false,
		placeholder: "https://linkedin.com/in/username",
		...overrides,
	}),

	// ------------------------------------------------- LOCATION FIELDS -----------------------------------------------

	city: (overrides = {}) => ({
		name: "city",
		label: "City",
		type: "text",
		required: false,
		placeholder: "Enter city name",
		...overrides,
	}),

	postcode: (overrides = {}) => ({
		name: "postcode",
		label: "Post Code",
		type: "text",
		required: false,
		placeholder: "Enter post code",
		...overrides,
	}),

	// Standard country field that requires countries to be passed in
	country: (countries = [], loading = false, overrides = {}) => ({
		name: "country",
		label: "Country",
		type: "select",
		required: false,
		options: countries,
		placeholder: loading ? "Loading countries..." : "Search and select a country...",
		isSearchable: true,
		isClearable: true,
		isDisabled: loading,
		...overrides,
	}),

	// Auto-loading country field component
	countryAuto: (overrides = {}) => {
		// This creates a field definition that includes the hook for auto-loading
		return {
			name: "country",
			label: "Country",
			type: "select",
			required: false,
			placeholder: "Loading countries...",
			isSearchable: true,
			isClearable: true,
			isDisabled: true,
			autoLoad: true, // Flag to indicate this field auto-loads
			...overrides,
		};
	},

	// ------------------------------------------------- JOB FIELDS --------------------------------------------------

	jobTitle: (overrides = {}) => ({
		name: "title",
		label: "Job Title",
		type: "text",
		required: true,
		placeholder: "Enter job title",
		...overrides,
	}),

	salaryMin: (overrides = {}) => ({
		name: "salary_min",
		label: "Minimum Salary",
		type: "number",
		placeholder: "Enter minimum salary",
		step: "1000",
		...overrides,
	}),

	salaryMax: (overrides = {}) => ({
		name: "salary_max",
		label: "Maximum Salary",
		type: "number",
		placeholder: "Enter maximum salary",
		step: "1000",
		...overrides,
	}),

	personalRating: (overrides = {}) => ({
		name: "personal_rating",
		label: "Personal Rating (1-5)",
		type: "select",
		options: [
			{ value: 1, label: "1 - Poor" },
			{ value: 2, label: "2 - Fair" },
			{ value: 3, label: "3 - Good" },
			{ value: 4, label: "4 - Very Good" },
			{ value: 5, label: "5 - Excellent" },
		],
		...overrides,
	}),

	// ------------------------------------------------- INTERVIEW FIELDS --------------------------------------------

	interviewDate: (overrides = {}) => ({
		name: "date",
		label: "Interview Date & Time",
		type: "datetime-local",
		required: true,
		placeholder: "Select interview date and time",
		...overrides,
	}),

	interviewType: (overrides = {}) => ({
		name: "type",
		label: "Interview Type",
		type: "select",
		required: true,
		options: [
			{ value: "HR", label: "HR Interview" },
			{ value: "Technical", label: "Technical Interview" },
			{ value: "Management", label: "Management Interview" },
			{ value: "Panel", label: "Panel Interview" },
			{ value: "Phone", label: "Phone Interview" },
			{ value: "Video", label: "Video Interview" },
			{ value: "Assessment", label: "Assessment/Test" },
			{ value: "Final", label: "Final Interview" },
			{ value: "Other", label: "Other" },
		],
		placeholder: "Select interview type",
		...overrides,
	}),

	interviewNotes: (overrides = {}) => ({
		name: "note",
		label: "Interview Notes",
		type: "textarea",
		placeholder: "Add notes about the interview, questions asked, impressions, etc...",
		...overrides,
	}),

	// ------------------------------------------------- APPLICATION FIELDS -----------------------------------------

	applicationDate: (overrides = {}) => ({
		name: "date",
		label: "Application Date",
		type: "datetime-local",
		required: true,
		placeholder: "Select application date and time",
		...overrides,
	}),

	applicationStatus: (overrides = {}) => ({
		name: "status",
		label: "Application Status",
		type: "select",
		options: [
			{ value: "Applied", label: "Applied" },
			{ value: "Interview", label: "Interview" },
			{ value: "Rejected", label: "Rejected" },
			{ value: "Offer", label: "Offer" },
			{ value: "Withdrawn", label: "Withdrawn" },
		],
		required: true,
		...overrides,
	}),

	applicationUrl: (overrides = {}) => ({
		name: "url",
		label: "Application URL",
		type: "text",
		placeholder: "https://... (link to your application submission)",
		...overrides,
	}),

	// ------------------------------------------------- SELECT FIELDS WITH OPTIONS ---------------------------------

	company: (options = [], onAdd = null, overrides = {}) => ({
		name: "company_id",
		label: "Company",
		type: "select",
		required: true,
		placeholder: "Select or search company...",
		isSearchable: true,
		isClearable: true,
		options: options,
		...(onAdd && {
			addButton: {
				onClick: onAdd,
			},
		}),
		...overrides,
	}),

	location: (options = [], onAdd = null, overrides = {}) => ({
		name: "location_id",
		label: "Location",
		type: "select",
		placeholder: "Select or search location...",
		isSearchable: true,
		isClearable: true,
		options: options,
		...(onAdd && {
			addButton: {
				onClick: onAdd,
			},
		}),
		...overrides,
	}),

	keywords: (options = [], onAdd = null, overrides = {}) => ({
		name: "keywords",
		label: "Keywords/Tags",
		type: "multiselect",
		placeholder: "Select or search keywords...",
		isSearchable: true,
		options: options,
		...(onAdd && {
			addButton: {
				onClick: onAdd,
			},
		}),
		...overrides,
	}),

	contacts: (options = [], onAdd = null, overrides = {}) => ({
		name: "contacts",
		label: "Contacts",
		type: "multiselect",
		placeholder: "Select or search contacts...",
		isSearchable: true,
		options: options,
		...(onAdd && {
			addButton: {
				onClick: onAdd,
			},
		}),
		...overrides,
	}),

	interviewers: (options = [], onAdd = null, overrides = {}) => ({
		name: "interviewers",
		label: "Interviewers",
		type: "multiselect",
		isSearchable: true,
		options: options,
		...(onAdd && {
			addButton: {
				onClick: onAdd,
			},
		}),
		...overrides,
	}),

	jobApplication: (options = [], overrides = {}) => ({
		name: "jobapplication_id",
		label: "Job Application",
		type: "select",
		options: options,
		required: true,
		placeholder: "Select job application",
		isSearchable: true,
		...overrides,
	}),
};
