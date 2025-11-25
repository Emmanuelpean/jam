import { accessAttribute, findItemById } from "../../../utils/Utils";
import React, { JSX, useMemo, useState } from "react";
import { DataContextValue, useDataContext } from "../../../contexts/DataContext";
import { CompanyModal } from "../../modals/CompanyModal";
import { LocationModal } from "../../modals/LocationModal";
import { KeywordModal } from "../../modals/KeywordModal";
import { PersonModal } from "../../modals/PersonModal";
import { AggregatorModal } from "../../modals/AggregatorModal";
import { JobModal } from "../../modals/JobModal";
import { SelectWidgetPreviewConfig } from "../widgets/SelectWidget";
import { modalViewFields } from "../view/ModalFields";
import { JobData, PersonData } from "../../../services/Schemas";

export type SelectOption = {
	value: string;
	label: string;
	data?: any;
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
	getCompanyPreviewConfig: SelectWidgetPreviewConfig;
	getPersonPreviewConfig: SelectWidgetPreviewConfig;
	getLocationPreviewConfig: SelectWidgetPreviewConfig;
	getAggregatorPreviewConfig: SelectWidgetPreviewConfig;
}

interface DataFactories {
	companies?: () => any;
	locations?: () => any;
	keywords?: () => any;
	persons?: () => any;
	aggregators?: () => any;
	jobs?: () => any;
}

export const toSelectOptions = (
	data: any[],
	valueKey: string | ((item: any) => any) = "id",
	labelKey: string | ((item: any) => any) = "name",
): SelectOption[] => {
	return data.map(
		(item: any): SelectOption => ({
			value: typeof valueKey === "function" ? valueKey(item) : accessAttribute(item, valueKey),
			label: typeof labelKey === "function" ? labelKey(item) : accessAttribute(item, labelKey),
			data: item,
		}),
	);
};
export const useFormOptions = (dataFactories: DataFactories = {}): UseFormOptionsReturn => {
	const contextData: DataContextValue = useDataContext();

	const getCompanyPreviewConfig: SelectWidgetPreviewConfig = {
		enabled: true,
		fields: [modalViewFields.name({ isTitle: true }), modalViewFields.url(), [modalViewFields.description()]],
		getDataById: (id: number) => findItemById(contextData.companies, id),
	};

	const getPersonPreviewConfig: SelectWidgetPreviewConfig = {
		enabled: true,
		fields: [
			modalViewFields.name({ isTitle: true }),
			modalViewFields.email(),
			[modalViewFields.companyBadge(), modalViewFields.role()],
		],
		getDataById: (id: number) => findItemById(contextData.persons, id),
	};

	const getLocationPreviewConfig: SelectWidgetPreviewConfig = {
		enabled: true,
		fields: [modalViewFields.name({ isTitle: true }), modalViewFields.locationMap({ label: "" })],
		getDataById: (id: number) => findItemById(contextData.locations, id),
	};

	const getAggregatorPreviewConfig: SelectWidgetPreviewConfig = {
		enabled: true,
		fields: [modalViewFields.name({ isTitle: true }), modalViewFields.url()],
		getDataById: (id: number) => findItemById(contextData.aggregators, id),
	};

	const getJobLabel = (job: JobData): string => {
		if (job.company_id) {
			const company = findItemById(contextData.companies, job.company_id);
			if (company) {
				return `${job.title} (${company.name})`;
			}
		}
		return job.title;
	};

	const getPersonLabel = (person: PersonData): string => {
		if (person.company_id) {
			const company = findItemById(contextData.companies, person.company_id);
			if (company) {
				return `${person.name} (${company.name})`;
			}
		}
		return person.name;
	};

	// Modal states
	const [showCompanyModal, setShowCompanyModal] = useState<boolean>(false);
	const [showLocationModal, setShowLocationModal] = useState<boolean>(false);
	const [showKeywordModal, setShowKeywordModal] = useState<boolean>(false);
	const [showPersonModal, setShowPersonModal] = useState<boolean>(false);
	const [showAggregatorModal, setShowAggregatorModal] = useState<boolean>(false);
	const [showJobModal, setShowJobModal] = useState<boolean>(false);

	// Convert data to SelectOptions and memoize
	const companyOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.companies),
		[contextData.companies],
	);
	const locationOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.locations),
		[contextData.locations],
	);
	const keywordOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.keywords),
		[contextData.keywords],
	);
	const personOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.persons, "id", getPersonLabel),
		[contextData.persons],
	);
	const aggregatorOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.aggregators),
		[contextData.aggregators],
	);
	const jobOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.jobs, "id", getJobLabel),
		[contextData.jobs],
	);
	const countryOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.countries, "name", "name"),
		[contextData.countries],
	);
	const currencyOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.currencies, "code", "symbol"),
		[contextData.currencies],
	);
	const currencyNameOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.currencies, "code", "name"),
		[contextData.currencies],
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
		error: contextData.error as Error | null,
		companies: companyOptions,
		locations: locationOptions,
		keywords: keywordOptions,
		persons: personOptions,
		aggregators: aggregatorOptions,
		jobs: jobOptions,
		countries: countryOptions,
		currencies: currencyOptions,
		currencyNames: currencyNameOptions,
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
		getCompanyPreviewConfig,
		getPersonPreviewConfig,
		getLocationPreviewConfig,
		getAggregatorPreviewConfig,
	};
};
