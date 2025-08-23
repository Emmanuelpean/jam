import React, { useEffect, useState } from "react";
import { useAuth } from "../../../contexts/AuthContext";
import {
	aggregatorsApi,
	companiesApi,
	jobApplicationsApi,
	jobsApi,
	keywordsApi,
	locationsApi,
	personsApi,
} from "../../../services/Api.ts";
import { fetchCountries } from "../../../utils/CountryUtils.ts";
import { CompanyFormModal } from "../../modals/CompanyModal";
import { LocationFormModal } from "../../modals/LocationModal";
import { KeywordFormModal } from "../../modals/KeywordModal";
import { PersonFormModal } from "../../modals/PersonModal";
import { AggregatorFormModal } from "../../modals/AggregatorModal";
import { JobFormModal } from "../../modals/_JobModal";
import { JobApplicationFormModal } from "../../modals/JobApplicationModal";
import { THEMES } from "../../../utils/Theme.ts";
import { toSelectOptions } from "../../../utils/Utils.ts";

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

export const useFormOptions = (requiredOptions = []) => {
	const { token } = useAuth();
	const [companies, setCompanies] = useState([]);
	const [locations, setLocations] = useState([]);
	const [keywords, setKeywords] = useState([]);
	const [persons, setPersons] = useState([]);
	const [aggregators, setAggregators] = useState([]);
	const [jobs, setJobs] = useState([]);
	const [jobApplications, setJobApplications] = useState([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);

	// Modal states
	const [showCompanyModal, setShowCompanyModal] = useState(false);
	const [showLocationModal, setShowLocationModal] = useState(false);
	const [showKeywordModal, setShowKeywordModal] = useState(false);
	const [showPersonModal, setShowPersonModal] = useState(false);
	const [showAggregatorModal, setShowAggregatorModal] = useState(false);
	const [showJobModal, setShowJobModal] = useState(false);
	const [showJobApplicationModal, setShowJobApplicationModal] = useState(false);

	useEffect(() => {
		const fetchOptions = async () => {
			if (!token || requiredOptions.length === 0) return;

			setLoading(true);
			setError(null);

			try {
				const apiCalls = [];
				const optionTypes = [];

				// Only fetch what's needed
				if (requiredOptions.includes("companies")) {
					apiCalls.push(companiesApi.getAll(token));
					optionTypes.push("companies");
				}
				if (requiredOptions.includes("locations")) {
					apiCalls.push(locationsApi.getAll(token));
					optionTypes.push("locations");
				}
				if (requiredOptions.includes("keywords")) {
					apiCalls.push(keywordsApi.getAll(token));
					optionTypes.push("keywords");
				}
				if (requiredOptions.includes("persons")) {
					apiCalls.push(personsApi.getAll(token));
					optionTypes.push("persons");
				}
				if (requiredOptions.includes("aggregators")) {
					apiCalls.push(aggregatorsApi.getAll(token));
					optionTypes.push("aggregators");
				}
				if (requiredOptions.includes("jobs")) {
					apiCalls.push(jobsApi.getAll(token));
					optionTypes.push("jobs");
				}
				if (requiredOptions.includes("jobApplications")) {
					apiCalls.push(jobApplicationsApi.getAll(token));
					optionTypes.push("jobApplications");
				}

				const results = await Promise.all(apiCalls);

				// Set the data based on what was fetched
				results.forEach((data, index) => {
					const type = optionTypes[index];
					switch (type) {
						case "companies":
							setCompanies(toSelectOptions(data));
							break;
						case "locations":
							setLocations(toSelectOptions(data));
							break;
						case "keywords":
							setKeywords(toSelectOptions(data));
							break;
						case "persons":
							setPersons(toSelectOptions(data));
							break;
						case "aggregators":
							setAggregators(toSelectOptions(data));
							break;
						case "jobs":
							setJobs(toSelectOptions(data));
							break;
						case "jobApplications":
							setJobApplications(toSelectOptions(data, "id", "job.name"));
							break;
					}
				});
			} catch (err) {
				console.error("Error fetching form options:", err);
				setError(err);
			} finally {
				setLoading(false);
			}
		};

		fetchOptions().then(() => null);
	}, [token, JSON.stringify(requiredOptions)]);

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

	const openJobModal = () => setShowJobModal(true);
	const closeJobModal = () => setShowJobModal(false);

	const openJobApplicationModal = () => setShowJobApplicationModal(true);
	const closeJobApplicationModal = () => setShowJobApplicationModal(false);

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

	const handleJobAddSuccess = (newJob) => {
		const newOption = {
			value: newJob.id,
			label: newJob.title,
		};
		setJobs((prev) => [...prev, newOption]);
		closeJobModal();
	};

	const handleJobApplicationAddSuccess = (newJobApplication) => {
		const newOption = {
			value: newJobApplication.id,
			label: newJobApplication.title,
		};
		setJobApplications((prev) => [...prev, newOption]);
		closeJobApplicationModal();
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

	const renderJobModal = () => (
		<JobFormModal show={showJobModal} onHide={closeJobModal} onSuccess={handleJobAddSuccess} />
	);

	const renderJobApplicationModal = () => (
		<JobApplicationFormModal
			show={showJobApplicationModal}
			onHide={closeJobApplicationModal}
			onSuccess={handleJobApplicationAddSuccess}
		/>
	);

	return {
		loading,
		error,
		// Only return the data that was requested
		companies: requiredOptions.includes("companies") ? companies : [],
		locations: requiredOptions.includes("locations") ? locations : [],
		keywords: requiredOptions.includes("keywords") ? keywords : [],
		persons: requiredOptions.includes("persons") ? persons : [],
		aggregators: requiredOptions.includes("aggregators") ? aggregators : [],
		jobs: requiredOptions.includes("jobs") ? jobs : [],
		jobApplications: requiredOptions.includes("jobApplications") ? jobApplications : [],
		// All modal handlers (same as before)
		openCompanyModal,
		renderCompanyModal,
		openLocationModal,
		renderLocationModal,
		openKeywordModal,
		renderKeywordModal,
		openPersonModal,
		renderPersonModal,
		openAggregatorModal,
		renderAggregatorModal,
		openJobModal,
		renderJobModal,
		openJobApplicationModal,
		renderJobApplicationModal,
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

	datetime: (overrides = {}) => ({
		name: "date",
		label: "Date & Time",
		type: "datetime-local",
		required: true,
		placeholder: "Select date and time",
		...overrides,
	}),

	updateType: (overrides = {}) => ({
		name: "type",
		label: "Update Type",
		type: "select",
		required: true,
		options: [
			{ value: "received", label: "Received" },
			{ value: "sent", label: "Sent" },
		],
		...overrides,
	}),

	// ------------------------------------------------- USERS ------------------------------------------------

	appTheme: (overrides = {}) => ({
		name: "theme",
		label: "App Theme",
		type: "select",
		required: false,
		options: THEMES.map((theme) => ({ value: theme.key, label: theme.name })),
		...overrides,
	}),

	isAdmin: (overrides = {}) => ({
		name: "is_admin",
		label: "Admin",
		type: "checkbox",
		...overrides,
	}),

	password: (overrides = {}) => ({
		name: "password",
		label: "Password",
		type: "password",
		required: true,
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
		type: "salary",
		placeholder: "Enter minimum salary",
		step: "1000",
		...overrides,
	}),

	salaryMax: (overrides = {}) => ({
		name: "salary_max",
		label: "Maximum Salary",
		type: "salary",
		placeholder: "Enter maximum salary",
		step: "1000",
		...overrides,
	}),

	personalRating: (overrides = {}) => ({
		name: "personal_rating",
		label: "Personal Rating",
		type: "rating",
		required: false,
		maxRating: 5,
		...overrides,
	}),

	attendanceType: (overrides = {}) => ({
		name: "attendance_type",
		label: "Attendance Type",
		type: "select",
		options: [
			{ value: "on-site", label: "On-site" },
			{ value: "hybrid", label: "Hybrid" },
			{ value: "remote", label: "Remote" },
		],
		...overrides,
	}),

	interviewAttendanceType: (overrides = {}) => ({
		name: "attendance_type",
		label: "Attendance Type",
		type: "select",
		options: [
			{ value: "on-site", label: "On-site" },
			{ value: "remote", label: "Remote" },
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
		...formFields.datetime(),
		name: "date",
		label: "Application Date",
		required: true,
		...overrides,
	}),

	applicationStatus: (overrides = {}) => ({
		name: "status",
		label: "Application Status",
		type: "select",
		options: [
			{ value: "applied", label: "Applied" },
			{ value: "interview", label: "Interview" },
			{ value: "rejected", label: "Rejected" },
			{ value: "offer", label: "Offer" },
			{ value: "withdrawn", label: "Withdrawn" },
		],
		required: true,
		...overrides,
	}),

	applicationVia: (overrides = {}) => ({
		name: "applied_via",
		label: "Application Via",
		type: "select",
		options: [
			{ value: "aggregator", label: "Aggregator" },
			{ value: "email", label: "Email" },
			{ value: "phone", label: "Phone" },
			{ value: "other", label: "Other" },
		],
		...overrides,
	}),

	// ------------------------------------------- SELECT FIELDS WITH OPTIONS ------------------------------------------

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
		name: "job_application_id",
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
