import React, { useEffect, useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import {
	aggregatorsApi,
	apiHelpers,
	companiesApi,
	jobsApi,
	keywordsApi,
	locationsApi,
	personsApi,
} from "../../services/api";
import { fetchCountries } from "../../utils/CountryUtils";
import { CompanyFormModal } from "../modals/CompanyModal";
import { LocationFormModal } from "../modals/LocationModal";
import { KeywordFormModal } from "../modals/KeywordModal";
import { PersonFormModal } from "../modals/PersonModal";
import { AggregatorFormModal } from "../modals/AggregatorModal";

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

		loadCountries().then(() => null);
	}, []);

	return { countries, loading, error };
};

// Enhanced hook for fetching form options data with modal management
export const useFormOptions = () => {
	const { token } = useAuth();
	const [companies, setCompanies] = useState([]);
	const [locations, setLocations] = useState([]);
	const [keywords, setKeywords] = useState([]);
	const [persons, setPersons] = useState([]);
	const [aggregators, setAggregators] = useState([]);
	const [jobs, setJobs] = useState([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);

	// Modal states
	const [showCompanyModal, setShowCompanyModal] = useState(false);
	const [showLocationModal, setShowLocationModal] = useState(false);
	const [showKeywordModal, setShowKeywordModal] = useState(false);
	const [showPersonModal, setShowPersonModal] = useState(false);
	const [showAggregatorModal, setShowAggregatorModal] = useState(false);

	useEffect(() => {
		const fetchOptions = async () => {
			if (!token) return;

			setLoading(true);
			setError(null);

			try {
				const [companiesData, locationsData, keywordsData, personsData, aggregatorsData, jobsData] =
					await Promise.all([
						companiesApi.getAll(token),
						locationsApi.getAll(token),
						keywordsApi.getAll(token),
						personsApi.getAll(token),
						aggregatorsApi.getAll(token),
						jobsApi.getAll(token),
					]);

				setCompanies(apiHelpers.toSelectOptions(companiesData));
				setLocations(apiHelpers.toSelectOptions(locationsData));
				setKeywords(apiHelpers.toSelectOptions(keywordsData));
				setPersons(apiHelpers.toSelectOptions(personsData));
				setAggregators(apiHelpers.toSelectOptions(aggregatorsData));
				setJobs(apiHelpers.toSelectOptions(jobsData));
			} catch (err) {
				console.error("Error fetching form options:", err);
				setError(err);
			} finally {
				setLoading(false);
			}
		};

		fetchOptions().then(() => null);
	}, [token]);

	// Helper function to refresh a specific option type
	const refreshOptions = async (type) => {
		if (!token) return;

		try {
			let data;
			switch (type) {
				case "companies":
					data = await companiesApi.getAll(token);
					setCompanies(apiHelpers.toSelectOptions(data));
					break;
				case "locations":
					data = await locationsApi.getAll(token);
					setLocations(apiHelpers.toSelectOptions(data));
					break;
				case "keywords":
					data = await keywordsApi.getAll(token);
					setKeywords(apiHelpers.toSelectOptions(data));
					break;
				case "persons":
					data = await personsApi.getAll(token);
					setPersons(apiHelpers.toSelectOptions(data));
					break;
				case "aggregators":
					data = await aggregatorsApi.getAll(token);
					setAggregators(apiHelpers.toSelectOptions(data));
					break;
				case "jobs":
					data = await jobsApi.getAll(token);
					setJobs(apiHelpers.toSelectOptions(data));
					break;
				default:
					console.warn(`Unknown option type: ${type}`);
			}
		} catch (err) {
			console.error(`Error refreshing ${type}:`, err);
		}
	};

	// Modal handlers
	const openCompanyModal = () => setShowCompanyModal(true);
	const closeCompanyModal = () => setShowCompanyModal(false);

	const openLocationModal = () => setShowLocationModal(true);
	const closeLocationModal = () => setShowLocationModal(false);

	const openKeywordModal = () => setShowKeywordModal(true);
	const closeKeywordModal = () => setShowKeywordModal(false);

	const openPersonModal = () => setShowPersonModal(true);
	const closePersonModal = () => setShowPersonModal(false);

	const openAggregatorModal = () => setShowAggregatorModal(true);
	const closeAggregatorModal = () => setShowAggregatorModal(false);

	// Handle successful item creation
	const handleCompanyAddSuccess = (newCompany) => {
		const newOption = {
			value: newCompany.id,
			label: newCompany.name,
		};
		setCompanies((prev) => [...prev, newOption]);
		closeCompanyModal();
	};

	const handleLocationAddSuccess = (newLocation) => {
		const newOption = {
			value: newLocation.id,
			label: newLocation.name,
		};
		setLocations((prev) => [...prev, newOption]);
		closeLocationModal();
	};

	const handleKeywordAddSuccess = (newKeyword) => {
		const newOption = {
			value: newKeyword.id,
			label: newKeyword.name,
		};
		setKeywords((prev) => [...prev, newOption]);
		closeKeywordModal();
	};

	const handlePersonAddSuccess = (newPerson) => {
		const newOption = {
			value: newPerson.id,
			label: newPerson.name,
		};
		setPersons((prev) => [...prev, newOption]);
		closePersonModal();
	};

	const handleAggregatorAddSuccess = (newAggregator) => {
		const newOption = {
			value: newAggregator.id,
			label: newAggregator.name,
		};
		setAggregators((prev) => [...prev, newOption]);
		closeAggregatorModal();
	};

	// Render modal functions
	const renderCompanyModal = () => (
		<CompanyFormModal show={showCompanyModal} onHide={closeCompanyModal} onSuccess={handleCompanyAddSuccess} />
	);

	const renderLocationModal = () => (
		<LocationFormModal show={showLocationModal} onHide={closeLocationModal} onSuccess={handleLocationAddSuccess} />
	);

	const renderKeywordModal = () => (
		<KeywordFormModal show={showKeywordModal} onHide={closeKeywordModal} onSuccess={handleKeywordAddSuccess} />
	);

	const renderPersonModal = () => (
		<PersonFormModal show={showPersonModal} onHide={closePersonModal} onSuccess={handlePersonAddSuccess} />
	);

	const renderAggregatorModal = () => (
		<AggregatorFormModal
			show={showAggregatorModal}
			onHide={closeAggregatorModal}
			onSuccess={handleAggregatorAddSuccess}
		/>
	);

	return {
		companies,
		locations,
		keywords,
		persons,
		aggregators,
		jobs,
		loading,
		error,
		refreshOptions,
		// Company modal management
		openCompanyModal,
		renderCompanyModal,
		// Location modal management
		openLocationModal,
		renderLocationModal,
		// Keyword modal management
		openKeywordModal,
		renderKeywordModal,
		// Person modal management
		openPersonModal,
		renderPersonModal,
		// Aggregator modal management
		openAggregatorModal,
		renderAggregatorModal,
	};
};

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
		type: "text",
		required: false,
		placeholder: "person@company.com",
		validation: (value) => {
			if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
				return { isValid: false, message: "Please enter a valid email address" };
			}
		},
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
		validation: (value) => {
			if (value && !value.includes("linkedin.com")) {
				return { isValid: false, message: "Please enter a valid LinkedIn URL" };
			}
		},
		...overrides,
	}),

	role: (overrides = {}) => ({
		name: "role",
		label: "Role",
		type: "text",
		required: false,
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

	applicationVia: (overrides = {}) => ({
		name: "applied_via",
		label: "Application Via",
		type: "select",
		options: [
			{ value: "Aggregator", label: "Aggregator" },
			{ value: "Email", label: "Email" },
			{ value: "Phone", label: "Phone" },
			{ value: "Other", label: "Other" },
		],
		...overrides,
	}),

	// ------------------------------------------------- SELECT FIELDS WITH OPTIONS ---------------------------------

	company: (options = [], onAdd = null, overrides = {}) => ({
		name: "company_id",
		label: "Company",
		type: "select",
		required: false,
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
		label: "Tags",
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
		placeholder: "Select a job application",
		isSearchable: true,
		...overrides,
	}),

	job: (options = [], onAdd = null, overrides = {}) => ({
		name: "job_id",
		label: "Job",
		type: "select",
		required: true,
		placeholder: "Select a job",
		isSearchable: true,
		isClearable: false,
		options: options,
		...(onAdd && {
			addButton: {
				onClick: onAdd,
			},
		}),
		...overrides,
	}),

	aggregator: (options = [], onAdd = null, overrides = {}) => ({
		name: "aggregator_id",
		label: "Aggregator",
		type: "select",
		placeholder: "Select an aggregator",
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
};
