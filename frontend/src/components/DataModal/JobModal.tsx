import React, { forwardRef, ReactNode, useRef } from "react";
import DataModal, {
	DataModalHandle,
	Fields,
	JamDataModalProps,
	SectionConfig,
	TabConfig,
	ValidationErrors,
} from "./DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { getApplicationStatusBadgeClass } from "../rendering/view/Icons";
import { useAuth } from "../../contexts/AuthContext";
import { useFormOptions } from "../rendering/form/FormOptions";
import { convertToEndOfDay } from "../../utils/TimeUtils";
import { CompanyModal } from "./CompanyModal";
import { PersonModal } from "./PersonModal";
import { AggregatorModal } from "./AggregatorModal";
import { KeywordModal } from "./KeywordModal";
import { LocationModal } from "./LocationModal";
import { JobData, JobDataTransform } from "../../services/schemas/DataTables";

interface JobAndApplicationProps extends JamDataModalProps {
	defaultActiveTab?: "job" | "application";
}

export const JobModal = forwardRef<DataModalHandle, JobAndApplicationProps>(
	({ size = "xl", defaultActiveTab = "job" }: JobAndApplicationProps, ref) => {
		const locationModalRef = useRef<DataModalHandle>(null);
		const personModalRef = useRef<DataModalHandle>(null);
		const companyModalRef = useRef<DataModalHandle>(null);
		const aggregatorModalRef = useRef<DataModalHandle>(null);
		const keywordModalRef = useRef<DataModalHandle>(null);
		const { currentUser } = useAuth();
		const { companies, locations, keywords, persons, aggregators } = useFormOptions();

		const jobFormFields: Fields = [
			{
				type: "section",
				key: "basic-info",
				title: "Basic Information",
				icon: "bi-briefcase",
				fields: [
					formFields.jobTitle({ placeholder: "Python Software Engineer" }),
					[formFields.company(companies, companyModalRef), formFields.jobURl()],
				],
			} as SectionConfig,
			{
				type: "section",
				key: "location-schedule",
				title: "Location",
				icon: "bi-geo-alt",
				fields: [[formFields.attendanceType(), formFields.location(locations, locationModalRef)]],
			} as SectionConfig,
			{
				type: "section",
				key: "compensation",
				title: "Compensation & Priority",
				icon: "bi-currency-pound",
				fields: [
					[formFields.salaryMin({ placeholder: "35000" }), formFields.salaryMax({ placeholder: "45000" })],
					[formFields.personalRating(), formFields.deadline()],
				],
			} as SectionConfig,
			{
				type: "section",
				key: "source",
				title: "Source",
				icon: "bi-search",
				fields: [
					[
						formFields.sourceType(),
						formFields.aggregator(aggregators, aggregatorModalRef, null, null, {
							name: "source_aggregator_id",
							displayCondition: (formData: JobDataTransform): boolean => {
								return ["aggregator", "aggregator_email"].includes(formData.source_type || "");
							},
						}),
						formFields.recruiter(persons, personModalRef, null, null, {
							displayCondition: (formData: JobDataTransform): boolean => {
								return formData.source_type ? formData.source_type === "recruiter" : false;
							},
						}),
						formFields.company(companies, companyModalRef, null, null, {
							name: "recruitment_company_id",
							displayCondition: (formData: JobDataTransform): boolean => {
								return formData.source_type ? formData.source_type === "recruitment_company" : false;
							},
						}),
					],
				],
			} as SectionConfig,
			{
				type: "section",
				key: "tags-contacts",
				title: "Tags & Contacts",
				icon: "bi-tags",
				fields: [
					[formFields.keywords(keywords, keywordModalRef), formFields.contacts(persons, personModalRef)],
				],
			} as SectionConfig,
			{
				type: "section",
				key: "details",
				title: "Details",
				icon: "bi-card-text",
				fields: [
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
				],
			} as SectionConfig,
		];

		const jobViewFields: Fields = [
			{
				type: "section",
				key: "overview",
				title: "Overview",
				icon: "bi-briefcase",
				fields: [
					[modalViewFields.title({ isTitle: true })],
					[modalViewFields.companyBadge(), modalViewFields.locationBadge()],
				],
			} as SectionConfig,
			{
				type: "section",
				key: "details",
				title: "Details",
				icon: "bi-card-text",
				fields: [modalViewFields.description(), modalViewFields.note()],
			} as SectionConfig,
			{
				type: "section",
				key: "compensation",
				title: "Compensation & Priority",
				icon: "bi-currency-pound",
				fields: [
					[modalViewFields.salaryRange(), modalViewFields.personalRating()],
					[modalViewFields.deadline()],
				],
			} as SectionConfig,
			{
				type: "section",
				key: "source",
				title: "Source & Links",
				icon: "bi-search",
				fields: [
					[
						modalViewFields.sourceAggregatorBadge({
							displayCondition: (data: JobData): boolean => {
								return ["aggregator", "aggregator_email"].includes(data.source_type || "");
							},
						}),
						modalViewFields.recruiterBadge({
							displayCondition: (data: JobData): boolean => {
								return data.source_type === "recruiter";
							},
						}),
						modalViewFields.recruitmentCompanyBadge({
							displayCondition: (data: JobData): boolean => {
								return data.source_type === "recruitment_company";
							},
						}),
						modalViewFields.sourceType({
							displayCondition: (data: JobData): boolean => {
								return (
									data.source_type === null ||
									(data.source_type ? data.source_type === "other" : false)
								);
							},
						}),
						modalViewFields.jobUrl(),
					],
				],
			} as SectionConfig,
			{
				type: "section",
				key: "tags-contacts",
				title: "Tags & Contacts",
				icon: "bi-tags",
				fields: [
					[
						modalViewFields.keywordBadges(),
						modalViewFields.personBadges({}, ["view", "edit", "delete", "followup"]),
					],
				],
			} as SectionConfig,
		];

		const applicationFormFields: Fields = [
			{
				type: "section",
				key: "application-details",
				title: "Application Details",
				icon: "bi-send",
				fields: [
					[formFields.applicationDate(), formFields.applicationStatus()],
					[
						formFields.applicationVia(),
						formFields.aggregator(aggregators, aggregatorModalRef, null, null, {
							name: "application_aggregator_id",
							displayCondition: (formData: JobDataTransform): boolean => {
								return formData.applied_via ? formData.applied_via === "aggregator" : true;
							},
						}),
					],
					formFields.applicationUrl({ placeholder: "https://linkedin.com/application/453635" }),
				],
			} as SectionConfig,
			{
				type: "section",
				key: "application-notes",
				title: "Notes",
				icon: "bi-journal-text",
				fields: [
					formFields.note({
						placeholder:
							"The application process involves submitting an online application, followed by technical " +
							"assessments and interviews to evaluate coding skills, problem-solving ability, and cultural fit.",
						name: "application_note",
						label: "",
					}),
				],
			} as SectionConfig,
		];

		const applicationViewFields: Fields = [
			{
				type: "section",
				key: "application-details",
				title: "Application Details",
				icon: "bi-send",
				fields: [
					[modalViewFields.applicationDate(), modalViewFields.applicationStatus()],
					[modalViewFields.appliedViaBadge()],
					[modalViewFields.applicationUrl()],
				],
			} as SectionConfig,
			{
				type: "section",
				key: "application-notes",
				title: "Notes",
				icon: "bi-journal-text",
				fields: [modalViewFields.applicationNote()],
			} as SectionConfig,
			modalViewFields.interviewTable(),
			modalViewFields.updateTable(),
			modalViewFields.followupSnoozeDateTime(),
		];

		const transformData = (jobData: JobDataTransform): JobDataTransform => {
			return {
				title: jobData.title.trim(),
				description: jobData.description?.trim() || null,
				note: jobData.note?.trim() || null,
				url: jobData.url?.trim() || null,
				salary_min: Number(jobData.salary_min) || null,
				salary_max: Number(jobData.salary_max) || null,
				salary_currency: currentUser?.preferences.default_currency?.trim() || null,
				personal_rating: jobData.personal_rating || null,
				company_id: jobData.company_id || null,
				location_id: jobData.location_id || null,
				deadline: jobData.deadline ? convertToEndOfDay(jobData.deadline) : null,
				source_aggregator_id: jobData.source_aggregator_id || null,
				source_type: jobData.source_type?.trim() || null,
				recruiter_id: jobData.recruiter_id || null,
				recruitment_company_id: jobData.recruitment_company_id || null,
				keywords: jobData.keywords || [],
				contacts: jobData.contacts || [],
				application_date: jobData.application_date ? new Date(jobData.application_date) : null,
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
			if (formData.salary_min && isNaN(Number(formData.salary_min))) {
				errors.salary_min = "Minimum Salary must be a valid number";
			}
			if (formData.salary_max && isNaN(Number(formData.salary_max))) {
				errors.salary_max = "Maximum Salary must be a valid number";
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
				<DataModal
					ref={ref}
					transformFormData={transformData}
					entityType="job"
					size={size}
					tabs={tabs}
					defaultActiveTab={defaultActiveTab}
					validation={customValidation}
				/>

				<CompanyModal ref={companyModalRef} />
				<PersonModal ref={personModalRef} />
				<AggregatorModal ref={aggregatorModalRef} />
				<KeywordModal ref={keywordModalRef} />
				<LocationModal ref={locationModalRef} />
			</>
		);
	}
);
