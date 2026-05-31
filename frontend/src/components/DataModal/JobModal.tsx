import React, { forwardRef, ReactNode, useRef } from "react";
import DataModal, {
	DataModalHandle,
	Fields,
	JamDataModalProps,
	SectionConfig,
	TabConfig,
	ValidationErrors,
} from "./DataModal";
import { useFormFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { getApplicationStatusBadgeClass } from "../rendering/view/Icons";
import { useAuth } from "../../contexts/AuthContext";
import { useFormOptions } from "../rendering/form/FormOptions";
import { convertToEndOfDay } from "../../utils/TimeUtils";
import { CompanyModal } from "./CompanyModal";
import { PersonModal } from "./PersonModal";
import { AggregatorModal } from "./AggregatorModal";
import { KeywordModal } from "./KeywordModal";
import FollowUpModal, { FollowUpModalHandle } from "../FollowUpModal/FollowUpModal";
import { ActionButton } from "../rendering/form/ActionButton";
import { JobData, JobDataTransform } from "../../services/schemas/DataTables";

interface JobAndApplicationProps extends JamDataModalProps {
	defaultActiveTab?: "job" | "application";
}

export const JobModal = forwardRef<DataModalHandle<JobData>, JobAndApplicationProps>(
	({ size = "xl", defaultActiveTab = "job" }: JobAndApplicationProps, ref) => {
		const personModalRef = useRef<DataModalHandle>(null);
		const companyModalRef = useRef<DataModalHandle>(null);
		const aggregatorModalRef = useRef<DataModalHandle>(null);
		const keywordModalRef = useRef<DataModalHandle>(null);
		const followUpModalRef = useRef<FollowUpModalHandle>(null);
		const { currentUser } = useAuth();
		const {
			companies,
			keywords,
			persons,
			aggregators,
			getCompanyPreviewConfig,
			getPersonPreviewConfig,
			getAggregatorPreviewConfig,
		} = useFormOptions();
		const ff = useFormFields();

		const jobFormFields: Fields = [
			{
				type: "section",
				key: "basic-info",
				title: "Basic Information",
				icon: "bi-briefcase",
				fields: [
					ff.jobTitleField({ placeholder: "Python Software Engineer" }),
					[ff.companyField(companies, companyModalRef, null, getCompanyPreviewConfig), ff.jobUrlField()],
				],
			} as SectionConfig,
			{
				type: "section",
				key: "location-schedule",
				title: "Location",
				icon: "bi-geo-alt",
				fields: [[ff.attendanceTypeField(), ff.locationField()]],
			} as SectionConfig,
			{
				type: "section",
				key: "compensation",
				title: "Compensation & Priority",
				icon: "bi-currency-pound",
				fields: [
					[ff.salaryMinField(), ff.salaryMaxField()],
					[ff.personalRatingField(), ff.isFavouriteField(), ff.deadlineField()],
				],
			} as SectionConfig,
			{
				type: "section",
				key: "source",
				title: "Source",
				icon: "bi-search",
				fields: [
					ff.sourceGroupFields(
						aggregators,
						aggregatorModalRef,
						getAggregatorPreviewConfig,
						persons,
						personModalRef,
						getPersonPreviewConfig,
						companies,
						companyModalRef,
						getCompanyPreviewConfig
					),
				],
			} as SectionConfig,
			{
				type: "section",
				key: "tags-contacts",
				title: "Tags & Contacts",
				icon: "bi-tags",
				fields: [
					[
						ff.keywordsField(keywords, keywordModalRef),
						ff.contactsField(persons, personModalRef, null, getPersonPreviewConfig),
					],
				],
			} as SectionConfig,
			{
				type: "section",
				key: "details",
				title: "Details",
				icon: "bi-card-text",
				fields: [
					ff.descriptionField({
						placeholder:
							"We are seeking a Python Software Engineer to develop, optimise, and maintain scalable software " +
							"solutions that drive innovation and support our growing business needs.",
					}),
					ff.noteField({
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
					[modalViewFields.salaryRange(), modalViewFields.deadline()],
					[modalViewFields.personalRating(), modalViewFields.isFavourite()],
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
					[ff.applicationDateField(), ff.applicationStatusField()],
					[
						ff.applicationViaField(),
						ff.applicationAggregatorField(
							aggregators,
							aggregatorModalRef,
							null,
							getAggregatorPreviewConfig,
							{}
						),
					],
					ff.applicationUrlField({ placeholder: "https://linkedin.com/application/453635" }),
				],
			} as SectionConfig,
			{
				type: "section",
				key: "application-documents",
				title: "Documents",
				icon: "bi-paperclip",
				fields: [[ff.cvUploadField(), ff.coverLetterUploadField()]],
			} as SectionConfig,
			{
				type: "section",
				key: "application-notes",
				title: "Notes",
				icon: "bi-journal-text",
				fields: [
					ff.noteField({
						placeholder:
							"The application process involves submitting an online application, followed by technical " +
							"assessments and interviews to evaluate coding skills, problem-solving ability, and cultural fit.",
						key: "application_note",
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
				key: "application-documents",
				title: "Documents",
				icon: "bi-paperclip",
				fields: [[modalViewFields.applicationCvBadge(), modalViewFields.applicationCoverLetterBadge()]],
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
				is_favourite: jobData.is_favourite ?? false,
				description: jobData.description?.trim() || null,
				note: jobData.note?.trim() || null,
				url: jobData.url?.trim() || null,
				salary_min: Number(jobData.salary_min) || null,
				salary_max: Number(jobData.salary_max) || null,
				salary_currency: currentUser?.preferences.default_currency?.trim() || null,
				personal_rating: jobData.personal_rating || null,
				company_id: jobData.company_id || null,
				location: jobData.location?.trim() || null,
				deadline: jobData.deadline ? convertToEndOfDay(jobData.deadline) : null,
				source_aggregator_id: jobData.source_aggregator_id || null,
				source_type: jobData.source_type?.trim() || null,
				recruiter_id: jobData.recruiter_id || null,
				recruitment_company_id: jobData.recruitment_company_id || null,
				keywords: jobData.keywords || [],
				contacts: jobData.contacts || [],
				application_date: jobData.application_date,
				application_url: jobData.application_url?.trim() || null,
				application_status: jobData.application_status?.trim() || null,
				applied_via: jobData.applied_via?.trim() || null,
				application_aggregator_id: jobData.application_aggregator_id || null,
				application_note: jobData.application_note?.trim() || null,
				attendance_type: jobData.attendance_type?.trim() || null,
				cv_id: jobData.cv_id || null,
				cover_letter_id: jobData.cover_letter_id || null,
			};
		};

		const applicationTabTitle = (jobData: JobData): ReactNode => {
			return jobData?.application_status ? (
				<span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "0.4rem" }}>
					Job Application
					<span className={`badge ${getApplicationStatusBadgeClass(jobData.application_status)}`}>
						{jobData.application_status}
					</span>
				</span>
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
				<DataModal<JobData>
					ref={ref}
					transformFormData={transformData}
					entityType="job"
					size={size}
					tabs={tabs}
					defaultActiveTab={defaultActiveTab}
					extraViewFooterButtons={(activeTab: string | null, data) =>
						activeTab === "application" && data?.has_application ? (
							<ActionButton
								id="job-modal-follow-up-button"
								variant="primary"
								onClick={() => followUpModalRef.current?.show(data)}
								defaultText="Follow-up Email"
								defaultIcon="bi bi-envelope"
								fullWidth={false}
							/>
						) : null
					}
				/>

				<CompanyModal ref={companyModalRef} />
				<PersonModal ref={personModalRef} />
				<AggregatorModal ref={aggregatorModalRef} />
				<KeywordModal ref={keywordModalRef} />
				<FollowUpModal ref={followUpModalRef} />
			</>
		);
	}
);
