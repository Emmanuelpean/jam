import React, { JSX, useEffect, useState } from "react";
import { useAuth } from "../../../contexts/AuthContext";
import {
	aggregatorsApi,
	companiesApi,
	jobApplicationsApi,
	jobsApi,
	keywordsApi,
	locationsApi,
	personsApi,
} from "../../../services/Api";
import { fetchCountries } from "../../../utils/CountryUtils";
import { CompanyModal } from "../../modals/CompanyModal";
import { LocationModal } from "../../modals/LocationModal";
import { KeywordModal } from "../../modals/KeywordModal";
import { PersonModal } from "../../modals/PersonModal";
import { AggregatorModal } from "../../modals/AggregatorModal";
import { JobApplicationModal } from "../../modals/JobApplicationModal";
import { Theme, THEMES } from "../../../utils/Theme";
import { Overrides, SelectOption, toSelectOptions } from "../../../utils/Utils";
import { JobAndApplicationModal } from "../../modals/JobAndApplicationModal";

interface UseCountriesReturn {
	countries: SelectOption[];
	loading: boolean;
	error: Error | null;
}

interface UseFormOptionsReturn {
	loading: boolean;
	error: Error | null;
	companies: SelectOption[];
	locations: SelectOption[];
	keywords: SelectOption[];
	persons: SelectOption[];
	aggregators: SelectOption[];
	jobs: SelectOption[];
	jobApplications: SelectOption[];
	openCompanyModal: () => void;
	renderCompanyModal: () => JSX.Element;
	openLocationModal: () => void;
	renderLocationModal: () => JSX.Element;
	openKeywordModal: () => void;
	renderKeywordModal: () => JSX.Element;
	openPersonModal: () => void;
	renderPersonModal: () => JSX.Element;
	openAggregatorModal: () => void;
	renderAggregatorModal: () => JSX.Element;
	openJobModal: () => void;
	renderJobModal: () => JSX.Element;
	openJobApplicationModal: () => void;
	renderJobApplicationModal: () => JSX.Element;
}

interface FormField {
	name: string;
	label: string;
	type: string;
	required?: boolean;
	placeholder?: string;
	options?: SelectOption[];
	validation?: (value: string) => { isValid: boolean; message: string } | undefined;

	[key: string]: any;
}

export const useCountries = (): UseCountriesReturn => {
	const [countries, setCountries] = useState<SelectOption[]>([]);
	const [loading, setLoading] = useState<boolean>(true);
	const [error, setError] = useState<Error | null>(null);

	useEffect(() => {
		const loadCountries = async (): Promise<void> => {
			try {
				setLoading(true);
				const countriesList = await fetchCountries();
				setCountries(countriesList);
				setError(null);
			} catch (err) {
				console.error("Failed to load countries:", err);
				setError(err as Error);
			} finally {
				setLoading(false);
			}
		};

		loadCountries().then(() => null);
	}, []);

	return { countries, loading, error };
};

export const useFormOptions = (requiredOptions: string[] = []): UseFormOptionsReturn => {
	const { token } = useAuth();
	const [companies, setCompanies] = useState<SelectOption[]>([]);
	const [locations, setLocations] = useState<SelectOption[]>([]);
	const [keywords, setKeywords] = useState<SelectOption[]>([]);
	const [persons, setPersons] = useState<SelectOption[]>([]);
	const [aggregators, setAggregators] = useState<SelectOption[]>([]);
	const [jobs, setJobs] = useState<SelectOption[]>([]);
	const [jobApplications, setJobApplications] = useState<SelectOption[]>([]);
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<Error | null>(null);

	// Modal states
	const [showCompanyModal, setShowCompanyModal] = useState<boolean>(false);
	const [showLocationModal, setShowLocationModal] = useState<boolean>(false);
	const [showKeywordModal, setShowKeywordModal] = useState<boolean>(false);
	const [showPersonModal, setShowPersonModal] = useState<boolean>(false);
	const [showAggregatorModal, setShowAggregatorModal] = useState<boolean>(false);
	const [showJobModal, setShowJobModal] = useState<boolean>(false);
	const [showJobApplicationModal, setShowJobApplicationModal] = useState<boolean>(false);

	useEffect(() => {
		const fetchOptions = async (): Promise<void> => {
			if (!token || requiredOptions.length === 0) return;

			setLoading(true);
			setError(null);

			try {
				const apiCalls: Promise<any>[] = [];
				const optionTypes: string[] = [];

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
				results.forEach((data: any, index: number) => {
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
				setError(err as Error);
			} finally {
				setLoading(false);
			}
		};

		fetchOptions().then(() => null);
	}, [token, JSON.stringify(requiredOptions)]);

	// Modal handlers
	const openCompanyModal = (): void => setShowCompanyModal(true);
	const closeCompanyModal = (): void => setShowCompanyModal(false);

	const openLocationModal = (): void => setShowLocationModal(true);
	const closeLocationModal = (): void => setShowLocationModal(false);

	const openKeywordModal = (): void => setShowKeywordModal(true);
	const closeKeywordModal = (): void => setShowKeywordModal(false);

	const openPersonModal = (): void => setShowPersonModal(true);
	const closePersonModal = (): void => setShowPersonModal(false);

	const openAggregatorModal = (): void => setShowAggregatorModal(true);
	const closeAggregatorModal = (): void => setShowAggregatorModal(false);

	const openJobModal = (): void => setShowJobModal(true);
	const closeJobModal = (): void => setShowJobModal(false);

	const openJobApplicationModal = (): void => setShowJobApplicationModal(true);
	const closeJobApplicationModal = (): void => setShowJobApplicationModal(false);

	// Handle successful item creation
	const handleCompanyAddSuccess = (newCompany: any): void => {
		const newOption: SelectOption = toSelectOptions([newCompany])[0]!;
		setCompanies((prev) => [...prev, newOption]);
		closeCompanyModal();
	};

	const handleLocationAddSuccess = (newLocation: any): void => {
		const newOption: SelectOption = toSelectOptions([newLocation])[0]!;
		setLocations((prev) => [...prev, newOption]);
		closeLocationModal();
	};

	const handleKeywordAddSuccess = (newKeyword: any): void => {
		const newOption: SelectOption = toSelectOptions([newKeyword])[0]!;
		setKeywords((prev) => [...prev, newOption]);
		closeKeywordModal();
	};

	const handlePersonAddSuccess = (newPerson: any): void => {
		const newOption: SelectOption = toSelectOptions([newPerson])[0]!;
		setPersons((prev) => [...prev, newOption]);
		closePersonModal();
	};

	const handleAggregatorAddSuccess = (newAggregator: any): void => {
		const newOption: SelectOption = toSelectOptions([newAggregator])[0]!;
		setAggregators((prev) => [...prev, newOption]);
		closeAggregatorModal();
	};

	const handleJobAddSuccess = (newJob: any): void => {
		const newOption: SelectOption = toSelectOptions([newJob, "id", "title"])[0]!;
		setJobs((prev) => [...prev, newOption]);
		closeJobModal();
	};

	const handleJobApplicationAddSuccess = (newJobApplication: any): void => {
		const newOption: SelectOption = toSelectOptions([newJobApplication], "id", "title")[0]!;
		setJobApplications((prev) => [...prev, newOption]);
		closeJobApplicationModal();
	};

	// Render modal functions
	const renderCompanyModal = (): JSX.Element => (
		<CompanyModal
			show={showCompanyModal}
			onHide={closeCompanyModal}
			data={{}}
			id={null}
			onSuccess={handleCompanyAddSuccess}
			onDelete={() => {}}
			submode="add"
		/>
	);

	const renderLocationModal = (): JSX.Element => (
		<LocationModal
			show={showLocationModal}
			onHide={closeLocationModal}
			data={{}}
			id={null}
			onSuccess={handleLocationAddSuccess}
			onDelete={() => {}}
			submode="add"
		/>
	);

	const renderKeywordModal = (): JSX.Element => (
		<KeywordModal
			show={showKeywordModal}
			onHide={closeKeywordModal}
			data={{}}
			id={null}
			onSuccess={handleKeywordAddSuccess}
			onDelete={() => {}}
			submode="add"
		/>
	);

	const renderPersonModal = (): JSX.Element => (
		<PersonModal
			show={showPersonModal}
			onHide={closePersonModal}
			data={{}}
			id={null}
			onSuccess={handlePersonAddSuccess}
			onDelete={() => {}}
			submode="add"
		/>
	);

	const renderAggregatorModal = (): JSX.Element => (
		<AggregatorModal
			show={showAggregatorModal}
			onHide={closeAggregatorModal}
			data={{}}
			id={null}
			onSuccess={handleAggregatorAddSuccess}
			onDelete={() => {}}
			submode="add"
		/>
	);

	const renderJobModal = (): JSX.Element => (
		<JobAndApplicationModal
			show={showJobModal}
			onHide={closeJobModal}
			data={{}}
			id={null}
			// @ts-ignore
			onSuccess={handleJobAddSuccess}
			onDelete={() => {}}
			submode="add"
		/>
	);

	const renderJobApplicationModal = (): JSX.Element => (
		<JobApplicationModal
			show={showJobApplicationModal}
			onHide={closeJobApplicationModal}
			data={{}}
			id={null}
			onSuccess={handleJobApplicationAddSuccess}
			onDelete={() => {}}
			submode="add"
		/>
	);

	return {
		loading,
		error,
		companies: requiredOptions.includes("companies") ? companies : [],
		locations: requiredOptions.includes("locations") ? locations : [],
		keywords: requiredOptions.includes("keywords") ? keywords : [],
		persons: requiredOptions.includes("persons") ? persons : [],
		aggregators: requiredOptions.includes("aggregators") ? aggregators : [],
		jobs: requiredOptions.includes("jobs") ? jobs : [],
		jobApplications: requiredOptions.includes("jobApplications") ? jobApplications : [],
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

	title: (overrides: Overrides = {}): FormField => ({
		name: "title",
		label: "Title",
		type: "text",
		required: true,
		placeholder: "Enter title",
		...overrides,
	}),

	name: (overrides: Overrides = {}): FormField => ({
		name: "name",
		label: "Name",
		type: "text",
		required: true,
		placeholder: "Enter name",
		...overrides,
	}),

	description: (overrides: Overrides = {}): FormField => ({
		name: "description",
		label: "Description",
		type: "textarea",
		rows: 4,
		placeholder: "Enter description...",
		...overrides,
	}),

	note: (overrides: Overrides = {}): FormField => ({
		name: "note",
		label: "Notes",
		type: "textarea",
		rows: 4,
		placeholder: "Add your notes...",
		...overrides,
	}),

	url: (overrides: Overrides = {}): FormField => ({
		name: "url",
		label: "URL",
		type: "text",
		placeholder: "https://...",
		...overrides,
	}),

	datetime: (overrides: Overrides = {}): FormField => ({
		name: "date",
		label: "Date & Time",
		type: "datetime-local",
		required: true,
		placeholder: "Select date and time",
		...overrides,
	}),

	updateType: (overrides: Overrides = {}): FormField => ({
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

	appTheme: (overrides: Overrides = {}): FormField => ({
		name: "theme",
		label: "App Theme",
		type: "select",
		options: THEMES.map((theme: Theme): SelectOption => ({ value: theme.key, label: theme.name })),
		...overrides,
	}),

	isAdmin: (overrides: Overrides = {}): FormField => ({
		name: "is_admin",
		label: "Admin",
		type: "checkbox",
		...overrides,
	}),

	password: (overrides: Overrides = {}): FormField => ({
		name: "password",
		label: "Password",
		type: "password",
		required: true,
		...overrides,
	}),

	// ------------------------------------------------- PERSON FIELDS ------------------------------------------------

	firstName: (overrides: Overrides = {}): FormField => ({
		name: "first_name",
		label: "First Name",
		type: "text",
		required: true,
		placeholder: "Enter first name",
		...overrides,
	}),

	lastName: (overrides: Overrides = {}): FormField => ({
		name: "last_name",
		label: "Last Name",
		type: "text",
		required: true,
		placeholder: "Enter last name",
		...overrides,
	}),

	email: (overrides: Overrides = {}): FormField => ({
		name: "email",
		label: "Email",
		type: "text",
		placeholder: "person@company.com",
		validation: (value: string) => {
			if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
				return { isValid: false, message: "Please enter a valid email address" };
			}
		},
		...overrides,
	}),

	phone: (overrides: Overrides = {}): FormField => ({
		name: "phone",
		label: "Phone",
		type: "tel",
		placeholder: "+44 20 7946 0958",
		...overrides,
	}),

	linkedinUrl: (overrides: Overrides = {}): FormField => ({
		name: "linkedin_url",
		label: "LinkedIn Profile",
		type: "text",
		placeholder: "https://linkedin.com/in/username",
		validation: (value: string) => {
			if (value && !value.includes("linkedin.com")) {
				return { isValid: false, message: "Please enter a valid LinkedIn URL" };
			}
		},
		...overrides,
	}),

	role: (overrides: Overrides = {}): FormField => ({
		name: "role",
		label: "Role",
		type: "text",
		...overrides,
	}),

	// ------------------------------------------------- LOCATION FIELDS -----------------------------------------------

	city: (overrides: Overrides = {}): FormField => ({
		name: "city",
		label: "City",
		type: "text",
		placeholder: "Enter city name",
		...overrides,
	}),

	postcode: (overrides: Overrides = {}): FormField => ({
		name: "postcode",
		label: "Post Code",
		type: "text",
		placeholder: "Enter post code",
		...overrides,
	}),

	country: (countries: SelectOption[] = [], overrides: Overrides = {}): FormField => ({
		name: "country",
		label: "Country",
		type: "select",
		options: countries,
		placeholder: "Search and select a country...",
		isSearchable: true,
		isClearable: true,
		...overrides,
	}),

	// ------------------------------------------------- JOB FIELDS --------------------------------------------------

	jobTitle: (overrides: Overrides = {}): FormField => ({
		name: "title",
		label: "Job Title",
		type: "text",
		required: true,
		placeholder: "Enter job title",
		...overrides,
	}),

	salaryMin: (overrides: Overrides = {}): FormField => ({
		name: "salary_min",
		label: "Minimum Salary",
		type: "salary",
		placeholder: "Enter minimum salary",
		step: "1000",
		...overrides,
	}),

	salaryMax: (overrides: Overrides = {}): FormField => ({
		name: "salary_max",
		label: "Maximum Salary",
		type: "salary",
		placeholder: "Enter maximum salary",
		step: "1000",
		...overrides,
	}),

	personalRating: (overrides: Overrides = {}): FormField => ({
		name: "personal_rating",
		label: "Personal Rating",
		type: "rating",
		maxRating: 5,
		...overrides,
	}),

	attendanceType: (overrides: Overrides = {}): FormField => ({
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

	interviewAttendanceType: (overrides: Overrides = {}): FormField => ({
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

	interviewType: (overrides: Overrides = {}): FormField => ({
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

	applicationDate: (overrides: Overrides = {}): FormField => ({
		...formFields.datetime(),
		name: "date",
		label: "Application Date",
		required: true,
		...overrides,
	}),

	applicationStatus: (overrides: Overrides = {}): FormField => ({
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

	applicationVia: (overrides: Overrides = {}): FormField => ({
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

	company: (
		options: SelectOption[] = [],
		onAdd: (() => void) | null = null,
		overrides: Overrides = {},
	): FormField => ({
		name: "company_id",
		label: "Company",
		type: "select",
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

	location: (
		options: SelectOption[] = [],
		onAdd: (() => void) | null = null,
		overrides: Overrides = {},
	): FormField => ({
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

	keywords: (
		options: SelectOption[] = [],
		onAdd: (() => void) | null = null,
		overrides: Overrides = {},
	): FormField => ({
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

	contacts: (
		options: SelectOption[] = [],
		onAdd: (() => void) | null = null,
		overrides: Overrides = {},
	): FormField => ({
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

	interviewers: (
		options: SelectOption[] = [],
		onAdd: (() => void) | null = null,
		overrides: Overrides = {},
	): FormField => ({
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

	jobApplication: (options: SelectOption[] = [], overrides: Overrides = {}): FormField => ({
		name: "job_application_id",
		label: "Job Application",
		type: "select",
		options: options,
		required: true,
		placeholder: "Select a job application",
		isSearchable: true,
		...overrides,
	}),

	job: (options: SelectOption[] = [], onAdd: (() => void) | null = null, overrides: Overrides = {}): FormField => ({
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

	aggregator: (
		options: SelectOption[] = [],
		onAdd: (() => void) | null = null,
		overrides: Overrides = {},
	): FormField => ({
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
