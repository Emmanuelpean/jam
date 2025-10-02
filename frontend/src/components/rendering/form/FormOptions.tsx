import { SelectOption, toSelectOptions } from "../../../utils/Utils";
import React, { JSX, useEffect, useState } from "react";
import { useAuth } from "../../../contexts/AuthContext";
import { aggregatorsApi, companiesApi, jobsApi, keywordsApi, locationsApi, personsApi } from "../../../services/Api";
import { fetchCountries } from "../../../utils/CountryUtils";
import { CompanyModal } from "../../modals/CompanyModal";
import { LocationModal } from "../../modals/LocationModal";
import { KeywordModal } from "../../modals/KeywordModal";
import { PersonModal } from "../../modals/PersonModal";
import { AggregatorModal } from "../../modals/AggregatorModal";
import { JobModal } from "../../modals/JobModal";

interface UseFormOptionsReturn {
	loading: boolean;
	error: Error | null;
	companies: SelectOption[];
	locations: SelectOption[];
	keywords: SelectOption[];
	persons: SelectOption[];
	aggregators: SelectOption[];
	jobs: SelectOption[];
	countries: SelectOption[];
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
}

export const useFormOptions = (requiredOptions: string[] = []): UseFormOptionsReturn => {
	const { token } = useAuth();
	const [companies, setCompanies] = useState<SelectOption[]>([]);
	const [locations, setLocations] = useState<SelectOption[]>([]);
	const [keywords, setKeywords] = useState<SelectOption[]>([]);
	const [persons, setPersons] = useState<SelectOption[]>([]);
	const [aggregators, setAggregators] = useState<SelectOption[]>([]);
	const [jobs, setJobs] = useState<SelectOption[]>([]);
	const [countries, setCountries] = useState<SelectOption[]>([]);
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<Error | null>(null);

	// Modal states
	const [showCompanyModal, setShowCompanyModal] = useState<boolean>(false);
	const [showLocationModal, setShowLocationModal] = useState<boolean>(false);
	const [showKeywordModal, setShowKeywordModal] = useState<boolean>(false);
	const [showPersonModal, setShowPersonModal] = useState<boolean>(false);
	const [showAggregatorModal, setShowAggregatorModal] = useState<boolean>(false);
	const [showJobModal, setShowJobModal] = useState<boolean>(false);

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
				if (requiredOptions.includes("countries")) {
					apiCalls.push(fetchCountries());
					optionTypes.push("countries");
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
						case "countries":
							setCountries(data);
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

	// Render modal functions
	const renderCompanyModal = (): JSX.Element => (
		<CompanyModal
			show={showCompanyModal}
			onHide={closeCompanyModal}
			onSuccess={handleCompanyAddSuccess}
			submode="add"
		/>
	);

	const renderLocationModal = (): JSX.Element => (
		<LocationModal
			show={showLocationModal}
			onHide={closeLocationModal}
			onSuccess={handleLocationAddSuccess}
			submode="add"
		/>
	);

	const renderKeywordModal = (): JSX.Element => (
		<KeywordModal
			show={showKeywordModal}
			onHide={closeKeywordModal}
			onSuccess={handleKeywordAddSuccess}
			submode="add"
		/>
	);

	const renderPersonModal = (): JSX.Element => (
		<PersonModal
			show={showPersonModal}
			onHide={closePersonModal}
			onSuccess={handlePersonAddSuccess}
			submode="add"
		/>
	);

	const renderAggregatorModal = (): JSX.Element => (
		<AggregatorModal
			show={showAggregatorModal}
			onHide={closeAggregatorModal}
			onSuccess={handleAggregatorAddSuccess}
			submode="add"
		/>
	);

	const renderJobModal = (): JSX.Element => (
		<JobModal show={showJobModal} onHide={closeJobModal} onSuccess={handleJobAddSuccess} submode="add" />
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
		countries: requiredOptions.includes("countries") ? countries : [],
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
	};
};
