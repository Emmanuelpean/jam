import React, { useCallback, useMemo, useState } from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields, useFormOptions } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { getApplicationStatusBadgeClass } from "../rendering/view/ViewRenders";

export const JobAndApplicationModal = ({
	show,
	onHide,
	data,
	onJobSuccess,
	onApplicationSuccess,
	onJobDelete,
	onApplicationDelete,
	submode = "view",
	size = "xl",
}) => {
	// Track current form data for conditional fields
	const [currentApplicationFormData, setCurrentApplicationFormData] = useState({});

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
	const handleApplicationFormDataChange = useCallback((newFormData) => {
		setCurrentApplicationFormData((prev) => ({
			...prev,
			...newFormData,
		}));
	}, []);

	// Job form fields
	const jobFormFieldsArray = [
		formFields.jobTitle(),
		[formFields.company(companies, openCompanyModal), formFields.location(locations, openLocationModal)],
		[formFields.keywords(keywords, openKeywordModal), formFields.contacts(persons, openPersonModal)],
		[formFields.attendanceType(), formFields.url({ label: "Job URL" })],
		[formFields.salaryMin(), formFields.salaryMax(), formFields.personalRating()],
		formFields.description(),
		formFields.note(),
	];

	const jobViewFieldsArray = [
		[viewFields.title({ isTitle: true })],
		[viewFields.company(), viewFields.location()],
		viewFields.description(),
		[viewFields.salaryRange(), viewFields.personalRating()],
		viewFields.url({ label: "Job URL" }),
		[viewFields.keywords(), viewFields.persons()],
	];

	const applicationFormFieldsArray = useMemo(() => {
		return [
			[formFields.applicationDate(), formFields.applicationStatus()],
			[
				formFields.applicationVia(),
				...(currentApplicationFormData?.applied_via === "aggregator"
					? [formFields.aggregator(aggregators, openAggregatorModal)]
					: []),
			],
			formFields.url(),
			formFields.note({
				placeholder: "Add notes about your application process, interview details, etc...",
			}),
		];
	}, [currentApplicationFormData.applied_via, openAggregatorModal, aggregators]);

	const applicationViewFieldsArray = useMemo(() => {
		const baseFields = [
			[viewFields.date(), viewFields.status()],
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

	const transformJobData = (jobData) => {
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
			keywords: jobData.keywords?.map((item) => item.id || item) || [],
			contacts: jobData.contacts?.map((item) => item.id || item) || [],
		};
	};

	const transformApplicationData = (jobApplicationData) => {
		return {
			date: new Date(jobApplicationData.date).toISOString(),
			url: jobApplicationData.url?.trim() || null,
			status: jobApplicationData.status,
			job_id: jobApplicationData.job_id || data?.id,
			applied_via: jobApplicationData.applied_via,
			aggregator_id: jobApplicationData.aggregator_id,
			note: jobApplicationData.note?.trim() || null,
		};
	};

	const applicationTabTitle = data?.job_application ? (
		<>
			Job Application{" "}
			<span className={`badge ${getApplicationStatusBadgeClass(data.job_application.status)} badge`}>
				{data.job_application.status}
			</span>
		</>
	) : (
		"Create Job Application"
	);
	const applicationSubmode = data?.job_application ? submode : "add";

	const tabs = [
		{
			key: "job",
			title: "Job Details",
			mode: "formview",
			submode: submode,
			data: data || {},
			fields: {
				form: jobFormFieldsArray,
				view: jobViewFieldsArray,
			},
			endpoint: "jobs",
			onSuccess: onJobSuccess,
			onDelete: onJobDelete,
			transformFormData: transformJobData,
		},
		{
			key: "application",
			title: applicationTabTitle,
			mode: "formview",
			submode: applicationSubmode,
			data: data?.job_application || {},
			fields: {
				form: applicationFormFieldsArray,
				view: applicationViewFieldsArray,
			},
			endpoint: "jobapplications",
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
				size={size}
				tabs={tabs}
				defaultActiveTab="job"
			/>

			{renderCompanyModal()}
			{renderLocationModal()}
			{renderKeywordModal()}
			{renderPersonModal()}
			{renderAggregatorModal()}
		</>
	);
};

export const JobAndApplicationFormModal = (props) => {
	const submode = props.isEdit || props.interview?.id ? "edit" : "add";
	return <JobAndApplicationModal {...props} submode={submode} />;
};

export const JobAndApplicationViewModal = (props) => (
	<JobAndApplicationModal {...props} interview={props.item} submode="view" />
);
