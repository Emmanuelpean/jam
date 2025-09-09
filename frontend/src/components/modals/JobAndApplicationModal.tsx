import React, { useMemo, useState } from "react";
import GenericModal, { TabConfig } from "./GenericModal/GenericModal";
import { formFields, useFormOptions } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { getApplicationStatusBadgeClass } from "../rendering/view/ViewRenders";
import { DataModalProps } from "./AggregatorModal";
import { JobData } from "../../services/Schemas";

interface JobAndApplicationProps extends DataModalProps {
	onSuccess?: (data: any) => void;
	onDelete?: ((item: any) => Promise<void>) | null;
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
	onSuccess,
	onDelete,
	submode = "view",
	size = "xl",
	defaultActiveTab = "job",
}) => {
	// Track current form data for conditional fields
	const [currentApplicationFormData, setCurrentApplicationFormData] = useState<ApplicationFormData>({});
	console.log("Modal data", data);
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

	const handleFormDataChange = (data: any) => {
		setCurrentApplicationFormData(data);
	};

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
		viewFields.note(),
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
					? [formFields.aggregator(aggregators, openAggregatorModal, { name: "application_aggregator_id" })]
					: []),
			],
			formFields.applicationUrl(),
			formFields.note({
				placeholder: "Add notes about your application process, interview details, etc...",
				name: "application_note",
			}),
		];
	}, [currentApplicationFormData.applied_via, openAggregatorModal, aggregators]);

	const applicationViewFields = [
		[viewFields.applicationDate(), viewFields.applicationStatus()],
		[viewFields.appliedVia()],
		[viewFields.applicationUrl()],
		viewFields.applicationNote(),
		viewFields.interviews(),
		viewFields.updates(),
	];

	const transformData = (jobData: JobData) => {
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
			keywords: jobData.keywords?.map((item) => (typeof item === "object" && item.id ? item.id : item)) || [],
			contacts: jobData.contacts?.map((item) => (typeof item === "object" && item.id ? item.id : item)) || [],
			application_date: jobData.application_date ? new Date(jobData.application_date).toISOString() : null,
			application_url: jobData.application_url?.trim() || null,
			application_status: jobData.application_status?.trim() || null,
			applied_via: jobData.applied_via?.trim() || null,
			application_aggregator_id: jobData.application_aggregator_id || null,
			application_note: jobData.application_note?.trim() || null,
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

	const tabs: TabConfig[] = [
		{
			key: "job",
			title: "Job Details",
			fields: {
				form: jobFormFields,
				view: jobViewFields,
			},
		},
		{
			key: "application",
			title: applicationTabTitle,
			fields: {
				form: applicationFormFields,
				view: applicationViewFields,
			},
		},
	];

	return (
		<>
			<GenericModal
				show={show}
				onHide={onHide}
				data={data}
				submode={submode}
				onDelete={onDelete}
				onSuccess={onSuccess}
				transformFormData={transformData}
				itemName="Job & Application"
				endpoint="jobs"
				size={size}
				tabs={tabs}
				id={id}
				defaultActiveTab={defaultActiveTab}
				fields={{ form: [], view: [] }}
				onFormDataChange={handleFormDataChange}
			/>

			{renderCompanyModal()}
			{renderLocationModal()}
			{renderKeywordModal()}
			{renderPersonModal()}
			{renderAggregatorModal()}
		</>
	);
};
