import React, { useCallback, useMemo, useState } from "react";
import GenericModal, { TabConfig } from "./GenericModal/GenericModal";
import { formFields, useFormOptions } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { getApplicationStatusBadgeClass } from "../rendering/view/ViewRenders";
import { DataModalProps } from "./AggregatorModal";
import { JobData } from "../../services/Schemas";

interface JobAndApplicationProps extends DataModalProps {
	onJobSuccess?: (data: any) => void;
	onApplicationSuccess?: (data: any) => void;
	onJobDelete?: ((item: any) => Promise<void>) | null;
	onApplicationDelete?: ((item: any) => Promise<void>) | null;
	defaultActiveTab?: "job" | "application";
}

interface ApplicationFormData {
	applied_via?: string;

	[key: string]: any;
}

export const JobAndApplicationModal: React.FC<JobAndApplicationProps> = ({
	show,
	onHide,
	data,
	id,
	onJobSuccess,
	onApplicationSuccess,
	onJobDelete,
	onApplicationDelete,
	submode = "view",
	size = "xl",
	defaultActiveTab = "job",
}) => {
	// Track current form data for conditional fields
	const [currentApplicationFormData, setCurrentApplicationFormData] = useState<ApplicationFormData>({});

	// Get form options for both job and application
	const {
		companies,
		locations,
		keywords,
		persons,
		aggregators,
		openCompanyModal,
		openLocationModal,
		openKeywordModal,
		openPersonModal,
		openAggregatorModal,
		renderCompanyModal,
		renderLocationModal,
		renderKeywordModal,
		renderPersonModal,
		renderAggregatorModal,
	} = useFormOptions(["companies", "locations", "keywords", "persons", "aggregators"]);

	// Handler for application form data changes
	const handleApplicationFormDataChange = useCallback((newFormData: ApplicationFormData) => {
		setCurrentApplicationFormData((prev) => ({
			...prev,
			...newFormData,
		}));
	}, []);

	const jobFormFields = [
		formFields.jobTitle(),
		[formFields.company(companies, openCompanyModal), formFields.location(locations, openLocationModal)],
		[formFields.keywords(keywords, openKeywordModal), formFields.contacts(persons, openPersonModal)],
		[formFields.attendanceType(), formFields.url({ label: "Job URL" })],
		[formFields.salaryMin(), formFields.salaryMax(), formFields.personalRating()],
		formFields.description(),
		formFields.note(),
	];

	const jobViewFields = [
		[viewFields.title({ isTitle: true })],
		[viewFields.company(), viewFields.location()],
		viewFields.description(),
		[viewFields.salaryRange(), viewFields.personalRating()],
		viewFields.url({ label: "Job URL" }),
		[viewFields.keywords(), viewFields.persons()],
	];

	const applicationFormFields = useMemo(() => {
		return [
			[formFields.applicationDate(), formFields.applicationStatus()],
			[
				formFields.applicationVia(),
				...(currentApplicationFormData?.applied_via === "aggregator"
					? [formFields.aggregator(aggregators, openAggregatorModal)]
					: []),
			],
			formFields.applicationUrl(),
			formFields.note({
				placeholder: "Add notes about your application process, interview details, etc...",
				name: "application_note",
			}),
		];
	}, [currentApplicationFormData.applied_via, openAggregatorModal, aggregators]);

	const applicationViewFields = useMemo(() => {
		const baseFields = [
			[viewFields.applicationDate(), viewFields.applicationStatus()],
			[viewFields.appliedVia()],
			[viewFields.url({ label: "Application URL" })],
			viewFields.note(),
		];

		if (data?.job_application?.id) {
			baseFields.push(viewFields.interviews());
			baseFields.push(viewFields.updates());
		}

		return baseFields;
	}, [data?.job_application?.id]);

	const transformJobData = (jobData: JobData) => {
		return {
			title: jobData.title.trim(),
			description: jobData.description?.trim() || null,
			note: jobData.note?.trim() || null,
			url: jobData.url?.trim() || null,
			salary_min: jobData.salary_min || null,
			salary_max: jobData.salary_max || null,
			personal_rating: jobData.personal_rating || null,
			company_id: jobData.company_id || null,
			location_id: jobData.location_id || null,
			keywords: jobData.keywords?.map((item: any) => item.id || item) || [], // TODO remove any
			contacts: jobData.contacts?.map((item: any) => item.id || item) || [],
		};
	};

	const transformApplicationData = (data: JobData) => {
		return {
			application_date: data.application_date ? new Date(data.application_date).toISOString() : null,
			application_url: data.application_url?.trim() || null,
			application_status: data.application_status,
			applied_via: data.applied_via,
			aggregator_id: data.application_aggregator_id,
			application_note: data.application_note?.trim() || null,
		};
	};

	const applicationTabTitle = data?.application_date ? (
		<>
			Job Application{" "}
			<span className={`badge ${getApplicationStatusBadgeClass(data.application_status)} badge`}>
				{data.application_status}
			</span>
		</>
	) : (
		"Create Job Application"
	);
	const applicationSubmode = data?.application_date ? submode : "add";

	const tabs: TabConfig[] = [
		{
			key: "job",
			title: "Job Details",
			submode: submode,
			data: data || {},
			fields: {
				form: jobFormFields,
				view: jobViewFields,
			},
			onSuccess: onJobSuccess,
			onDelete: onJobDelete,
			transformFormData: transformJobData,
		},
		{
			key: "application",
			title: applicationTabTitle,
			submode: applicationSubmode,
			data: data || {},
			fields: {
				form: applicationFormFields,
				view: applicationViewFields,
			},

			onSuccess: onApplicationSuccess,
			onDelete: onApplicationDelete,
			transformFormData: transformApplicationData,
			onFormDataChange: handleApplicationFormDataChange,
		},
	];

	return (
		<>
			<GenericModal
				show={show}
				onHide={onHide}
				itemName="Job & Application"
				endpoint="jobs"
				size={size}
				tabs={tabs}
				id={id}
				defaultActiveTab={defaultActiveTab}
				fields={{ form: [], view: [] }}
			/>

			{renderCompanyModal()}
			{renderLocationModal()}
			{renderKeywordModal()}
			{renderPersonModal()}
			{renderAggregatorModal()}
		</>
	);
};
