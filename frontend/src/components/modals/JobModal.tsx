import React, { ReactNode, useMemo } from "react";
import GenericModal, { DataModalProps, TabConfig, ValidationErrors } from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { getApplicationStatusBadgeClass } from "../rendering/view/ViewRenders";
import { JobData } from "../../services/Schemas";
import { jobsApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { useFormOptions } from "../rendering/form/FormOptions";

interface JobAndApplicationProps extends DataModalProps {
	defaultActiveTab?: "job" | "application";
}

export const JobModal: React.FC<JobAndApplicationProps> = ({
	show,
	onHide,
	data,
	id,
	onSuccess,
	onDelete,
	submode,
	size = "xl",
	defaultActiveTab = "job",
}) => {
	const { token } = useAuth();
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
	} = useFormOptions(show ? ["companies", "locations", "keywords", "persons", "aggregators"] : []);

	const jobFormFields = [
		formFields.jobTitle({ placeholder: "Python Software Engineer" }),
		[
			formFields.company(companies, openCompanyModal),
			formFields.url({ label: "Job URL", placeholder: "https://linkedin.com/jobs/453635" }),
		],
		[formFields.attendanceType(), formFields.location(locations, openLocationModal)],
		[formFields.keywords(keywords, openKeywordModal), formFields.contacts(persons, openPersonModal)],
		[formFields.salaryMin({ placeholder: "35000" }), formFields.salaryMax({ placeholder: "45000" })],
		[formFields.personalRating(), formFields.deadline()],
		formFields.description({
			placeholder:
				"We are seeking a Python Software Engineer to develop, optimise, and maintain scalable software " +
				"solutions that drive innovation and support our growing business needs.",
		}),
		formFields.note({
			placeholder:
				"This role offers a chance to apply Python expertise to build scalable solutions " +
				"while exploring opportunities for growth in automation, data analysis, and collaborative software development.",
		}),
	];

	const jobViewFields = [
		[modalViewFields.title({ isTitle: true })],
		[modalViewFields.companyBadge(), modalViewFields.locationBadge()],
		modalViewFields.description(),
		modalViewFields.note(),
		[modalViewFields.salaryRange(), modalViewFields.personalRating()],
		[modalViewFields.sourceBadge(), modalViewFields.url({ label: "Job URL" })],
		[modalViewFields.keywordBadges(), modalViewFields.personBadges()],
		modalViewFields.deadline(),
	];

	const applicationFormFields = useMemo(() => {
		return [
			[formFields.applicationDate(), formFields.applicationStatus()],
			[
				formFields.applicationVia(),
				formFields.aggregator(aggregators, openAggregatorModal, { name: "application_aggregator_id" }),
			],
			formFields.applicationUrl({ placeholder: "https://linkedin.com/application/453635" }),
			formFields.note({
				placeholder:
					"The application process involves submitting an online application, followed by technical " +
					"assessments and interviews to evaluate coding skills, problem-solving ability, and cultural fit.",
				name: "application_note",
			}),
		];
	}, [openAggregatorModal, aggregators]);

	const applicationViewFields = [
		[modalViewFields.applicationDate(), modalViewFields.applicationStatus()],
		[modalViewFields.appliedViaBadge()],
		[modalViewFields.applicationUrl()],
		modalViewFields.applicationNote(),
		modalViewFields.interviewTable(),
		modalViewFields.updateTable(),
	];

	const transformData = (jobData: JobData) => {
		console.log("AAAAA", jobData);
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
			deadline: jobData.deadline ? jobData.deadline + "T23:59:59" : null,
			keywords: jobData.keywords?.map((item) => (typeof item === "object" && item.id ? item.id : item)) || [],
			contacts: jobData.contacts?.map((item) => (typeof item === "object" && item.id ? item.id : item)) || [],
			application_date: jobData.application_date ? new Date(jobData.application_date).toISOString() : null,
			application_url: jobData.application_url?.trim() || null,
			application_status: jobData.application_status?.trim() || null,
			applied_via: jobData.applied_via?.trim() || null,
			application_aggregator_id: jobData.application_aggregator_id || null,
			application_note: jobData.application_note?.trim() || null,
			attendance_type: jobData.attendance_type?.trim() || null,
		};
	};

	const customValidation = async (formData: JobData): Promise<ValidationErrors> => {
		const errors: ValidationErrors = {};
		if (!token) {
			return errors;
		}
		if (formData.url) {
			const queryParams = { url: formData.url?.trim() };
			const matches = await jobsApi.getAll(token, queryParams);
			const duplicates = matches.filter((existing: JobData) => {
				return formData?.id !== existing.id;
			});

			if (duplicates.length > 0) {
				errors.url = `A Job with this URL already exists`;
			}
		}
		return errors;
	};

	const applicationTabTitle = (jobData: JobData): ReactNode => {
		return jobData?.application_status ? (
			<>
				Job Application{" "}
				<span className={`badge ${getApplicationStatusBadgeClass(jobData.application_status)} badge`}>
					{jobData.application_status}
				</span>
			</>
		) : (
			"Job Application"
		);
	};

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
				mode={submode}
				onDelete={onDelete}
				onSuccess={onSuccess}
				transformFormData={transformData}
				itemName="Job & Application"
				endpoint="jobs"
				size={size}
				tabs={tabs}
				id={id}
				defaultActiveTab={defaultActiveTab}
				validation={customValidation}
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
