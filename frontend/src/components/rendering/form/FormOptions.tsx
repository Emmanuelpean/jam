import { SelectOption, toSelectOptions } from "../../../utils/Utils";
import React, { JSX, useMemo, useState } from "react";
import { useDataContext } from "../../../contexts/DataContext";
import { CompanyModal } from "../../modals/CompanyModal";
import { LocationModal } from "../../modals/LocationModal";
import { KeywordModal } from "../../modals/KeywordModal";
import { PersonModal } from "../../modals/PersonModal";
import { AggregatorModal } from "../../modals/AggregatorModal";
import { JobModal } from "../../modals/JobModal";

interface UseFormOptionsReturn {
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
	const {
		companies: companiesData,
		locations: locationsData,
		keywords: keywordsData,
		persons: personsData,
		aggregators: aggregatorsData,
		jobs: jobsData,
		countries: countriesData,
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
	const companies = useMemo(() => toSelectOptions(companiesData), [companiesData]);
	const locations = useMemo(() => toSelectOptions(locationsData), [locationsData]);
	const keywords = useMemo(() => toSelectOptions(keywordsData), [keywordsData]);
	const persons = useMemo(() => toSelectOptions(personsData), [personsData]);
	const aggregators = useMemo(() => toSelectOptions(aggregatorsData), [aggregatorsData]);
	const jobs = useMemo(() => toSelectOptions(jobsData, "id", "title"), [jobsData]);
	const countries = useMemo(() => countriesData, [countriesData]);

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
