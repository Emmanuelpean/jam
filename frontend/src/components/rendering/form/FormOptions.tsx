import { SelectOption, toSelectOptions } from "../../../utils/Utils";
import React, { JSX, useMemo, useState } from "react";
import { useDataContext } from "../../../contexts/DataContext";
import { CompanyModal } from "../../modals/CompanyModal";
import { LocationModal } from "../../modals/LocationModal";
import { KeywordModal } from "../../modals/KeywordModal";
import { PersonModal } from "../../modals/PersonModal";
import { AggregatorModal } from "../../modals/AggregatorModal";
import { JobModal } from "../../modals/JobModal";
import currencies from "../../../data/currencies.json";
import countries from "../../../data/countries.json";

interface UseFormOptionsReturn {
	error: Error | null;
	companies: SelectOption[];
	locations: SelectOption[];
	keywords: SelectOption[];
	persons: SelectOption[];
	aggregators: SelectOption[];
	jobs: SelectOption[];
	countries: SelectOption[];
	currencies: SelectOption[];
	currencyNames: SelectOption[];
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
	const {
		companies: companiesData,
		locations: locationsData,
		keywords: keywordsData,
		persons: personsData,
		aggregators: aggregatorsData,
		jobs: jobsData,
		error,
	} = useDataContext();

	// Modal states
	const [showCompanyModal, setShowCompanyModal] = useState<boolean>(false);
	const [showLocationModal, setShowLocationModal] = useState<boolean>(false);
	const [showKeywordModal, setShowKeywordModal] = useState<boolean>(false);
	const [showPersonModal, setShowPersonModal] = useState<boolean>(false);
	const [showAggregatorModal, setShowAggregatorModal] = useState<boolean>(false);
	const [showJobModal, setShowJobModal] = useState<boolean>(false);

	// Convert data to SelectOptions and memoize
	const companyOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(companiesData),
		[companiesData],
	);
	const locationOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(locationsData),
		[locationsData],
	);
	const keywordOptions: SelectOption[] = useMemo((): SelectOption[] => toSelectOptions(keywordsData), [keywordsData]);
	const personOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(personsData, "id", "name_company"),
		[personsData],
	);
	const aggregatorOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(aggregatorsData),
		[aggregatorsData],
	);
	const jobOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(jobsData, "id", "name"),
		[jobsData],
	);
	const countryOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(countries, "name", "name"),
		[countries],
	);
	const currencyOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(currencies, "code", "symbol"),
		[currencies],
	);
	const currencyNameOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(currencies, "code", "name"),
		[currencies],
	);

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

	// Render modal functions
	const renderCompanyModal = (): JSX.Element => (
		<CompanyModal show={showCompanyModal} onHide={closeCompanyModal} onSuccess={closeCompanyModal} submode="add" />
	);

	const renderLocationModal = (): JSX.Element => (
		<LocationModal
			show={showLocationModal}
			onHide={closeLocationModal}
			onSuccess={closeCompanyModal}
			submode="add"
		/>
	);

	const renderKeywordModal = (): JSX.Element => (
		<KeywordModal show={showKeywordModal} onHide={closeKeywordModal} onSuccess={closeKeywordModal} submode="add" />
	);

	const renderPersonModal = (): JSX.Element => (
		<PersonModal show={showPersonModal} onHide={closePersonModal} onSuccess={closePersonModal} submode="add" />
	);

	const renderAggregatorModal = (): JSX.Element => (
		<AggregatorModal
			show={showAggregatorModal}
			onHide={closeAggregatorModal}
			onSuccess={closeAggregatorModal}
			submode="add"
		/>
	);

	const renderJobModal = (): JSX.Element => (
		<JobModal show={showJobModal} onHide={closeJobModal} onSuccess={closeJobModal} submode="add" />
	);

	return {
		error: error as Error | null,
		companies: requiredOptions.includes("companies") ? companyOptions : [],
		locations: requiredOptions.includes("locations") ? locationOptions : [],
		keywords: requiredOptions.includes("keywords") ? keywordOptions : [],
		persons: requiredOptions.includes("persons") ? personOptions : [],
		aggregators: requiredOptions.includes("aggregators") ? aggregatorOptions : [],
		jobs: requiredOptions.includes("jobs") ? jobOptions : [],
		countries: requiredOptions.includes("countries") ? countryOptions : [],
		currencies: requiredOptions.includes("currencies") ? currencyOptions : [],
		currencyNames: requiredOptions.includes("currencyNames") ? currencyNameOptions : [],
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
