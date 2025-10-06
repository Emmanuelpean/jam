import { SelectOption, toSelectOptions } from "../../../utils/Utils";
import React, { JSX, useMemo, useState } from "react";
import { useDataContext } from "../../../contexts/DataContext";
import { CompanyModal } from "../../modals/CompanyModal";
import { LocationModal } from "../../modals/LocationModal";
import { KeywordModal } from "../../modals/KeywordModal";
import { PersonModal } from "../../modals/PersonModal";
import { AggregatorModal } from "../../modals/AggregatorModal";
import { JobModal } from "../../modals/JobModal";

// Type for the factory function mapping
type DataFactoryMap = {
	companies?: () => any;
	locations?: () => any;
	keywords?: () => any;
	persons?: () => any;
	aggregators?: () => any;
	jobs?: () => any;
};

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

export const useFormOptions = (
	requiredOptions: string[] = [],
	dataFactories?: DataFactoryMap,
): UseFormOptionsReturn => {
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
	const companies: SelectOption[] = useMemo(() => toSelectOptions(companiesData), [companiesData]);
	const locations: SelectOption[] = useMemo(() => toSelectOptions(locationsData), [locationsData]);
	const keywords: SelectOption[] = useMemo(() => toSelectOptions(keywordsData), [keywordsData]);
	const persons: SelectOption[] = useMemo(() => toSelectOptions(personsData), [personsData]);
	const aggregators: SelectOption[] = useMemo(() => toSelectOptions(aggregatorsData), [aggregatorsData]);
	const jobs: SelectOption[] = useMemo(() => toSelectOptions(jobsData, "id", "name"), [jobsData]);
	const countries: SelectOption[] = useMemo(() => countriesData, [countriesData]);

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

	// Render modal functions with factory data support
	const renderCompanyModal = (): JSX.Element => {
		const initialData = dataFactories?.companies?.();
		return (
			<CompanyModal
				show={showCompanyModal}
				onHide={closeCompanyModal}
				onSuccess={closeCompanyModal}
				submode="add"
				data={initialData}
			/>
		);
	};

	const renderLocationModal = (): JSX.Element => {
		const initialData = dataFactories?.locations?.();
		return (
			<LocationModal
				show={showLocationModal}
				onHide={closeLocationModal}
				onSuccess={closeLocationModal}
				submode="add"
				data={initialData}
			/>
		);
	};

	const renderKeywordModal = (): JSX.Element => {
		const initialData = dataFactories?.keywords?.();
		return (
			<KeywordModal
				show={showKeywordModal}
				onHide={closeKeywordModal}
				onSuccess={closeKeywordModal}
				submode="add"
				data={initialData}
			/>
		);
	};

	const renderPersonModal = (): JSX.Element => {
		const initialData = dataFactories?.persons?.();
		return (
			<PersonModal
				show={showPersonModal}
				onHide={closePersonModal}
				onSuccess={closePersonModal}
				submode="add"
				data={initialData}
			/>
		);
	};

	const renderAggregatorModal = (): JSX.Element => {
		const initialData = dataFactories?.aggregators?.();
		return (
			<AggregatorModal
				show={showAggregatorModal}
				onHide={closeAggregatorModal}
				onSuccess={closeAggregatorModal}
				submode="add"
				data={initialData}
			/>
		);
	};

	const renderJobModal = (): JSX.Element => {
		const initialData = dataFactories?.jobs?.();
		return (
			<JobModal
				show={showJobModal}
				onHide={closeJobModal}
				onSuccess={closeJobModal}
				submode="add"
				data={initialData}
			/>
		);
	};

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
