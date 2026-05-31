import React, { forwardRef, JSX, ReactNode, useRef } from "react";
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
import { findClosestOption, findExactOption, useFormOptions } from "../rendering/form/FormOptions";
import { getApplicationStatusBadgeClass } from "../rendering/view/Icons";
import { useAuth } from "../../contexts/AuthContext";
import { CompanyModal } from "./CompanyModal";
import { PersonModal } from "./PersonModal";
import { AggregatorModal } from "./AggregatorModal";
import { KeywordModal } from "./KeywordModal";
import { JobData, JobDataTransform } from "../../services/schemas/DataTables";
import { convertToEndOfDay } from "../../utils/TimeUtils";
import { GeoLocationData } from "../../services/schemas/Base";
import { geolocationApi } from "../../services/api/Others";

export interface ExtensionJobData {
	title: string;
	url: string | null;
	description: string | null;
	salary_min: number | null;
	salary_max: number | null;
	attendance_type: string | null;
	source_type: string;
	company: string | null;
	location: string | null;
	platform: string | null;
	application_status: string | null;
	deadline?: string | null;
}

export const ExtensionJobModal = forwardRef<DataModalHandle<JobData>, JamDataModalProps>(
	({ size = "xl" }: JamDataModalProps, ref): JSX.Element => {
		const { token } = useAuth();
		const personModalRef = useRef<DataModalHandle>(null);
		const companyModalRef = useRef<DataModalHandle>(null);
		const aggregatorModalRef = useRef<DataModalHandle>(null);
		const keywordModalRef = useRef<DataModalHandle>(null);
		const { currentUser } = useAuth();
		const {
			companies,
			keywords,
			persons,
			aggregators,
			getPersonPreviewConfig,
			getAggregatorPreviewConfig,
			getCompanyPreviewConfig,
		} = useFormOptions();
		const ff = useFormFields();

		const transformInputData = async (data: ExtensionJobData) => {
			if (!data) return data;
			let geolocation: GeoLocationData | null;
			if (data.location && token) {
				geolocation = await geolocationApi.get(data.location, token);
			} else {
				geolocation = null;
			}
			return {
				...data,
				company_id: data.company ? findClosestOption(companies, data.company) : null,
				source_aggregator_id: data.platform ? findExactOption(aggregators, data.platform) : null,
				source_type: "aggregator",
				geolocation: geolocation,
			};
		};

		const jobFormFields: Fields = [
			{
				type: "section",
				key: "basic-info",
				title: "Basic Information",
				icon: "bi-briefcase",
				fields: [
					modalViewFields.title({ isTitle: true }),
					ff.scrapedCompanyField(
						companies,
						companyModalRef,
						(data: ExtensionJobData) => ({
							name: data.company,
						}),
						getCompanyPreviewConfig
					),
					ff.jobUrlField(),
				],
			} as SectionConfig,
			{
				type: "section",
				key: "location",
				title: "Location",
				icon: "bi-geo-alt",
				fields: [[ff.attendanceTypeField(), ff.locationField()], modalViewFields.geolocationMap()],
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
					modalViewFields.description(),
					ff.noteField({ placeholder: "Add any additional notes about this role..." }),
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
							getAggregatorPreviewConfig
						),
					],
					ff.applicationUrlField({ placeholder: "https://linkedin.com/jobs/123456/apply" }),
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
						placeholder: "Notes about the application process...",
						key: "application_note",
						label: "",
					}),
				],
			} as SectionConfig,
		];

		const transformFormData = (jobData: JobDataTransform): JobDataTransform => ({
			title: jobData.title.trim(),
			description: jobData.description?.trim() || null,
			note: jobData.note?.trim() || null,
			url: jobData.url?.trim() || null,
			salary_min: Number(jobData.salary_min) || null,
			salary_max: Number(jobData.salary_max) || null,
			salary_currency: currentUser?.preferences.default_currency?.trim() || null,
			personal_rating: jobData.personal_rating || null,
			is_favourite: jobData.is_favourite ?? false,
			company_id: jobData.company_id || null,
			location: jobData.location?.trim() || null,
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
			cv_id: jobData.cv_id || null,
			cover_letter_id: jobData.cover_letter_id || null,
		});

		const applicationTabTitle = (jobData: JobData): ReactNode =>
			jobData?.application_status ? (
				<>
					Job Application{" "}
					<span className={`badge ${getApplicationStatusBadgeClass(jobData.application_status)}`}>
						{jobData.application_status}
					</span>
				</>
			) : (
				"Job Application"
			);

		const tabs: TabConfig[] = [
			{
				key: "job",
				title: "Job Details",
				fields: { form: jobFormFields, view: [] },
			},
			{
				key: "application",
				title: applicationTabTitle,
				fields: { form: applicationFormFields, view: [] },
			},
		];

		return (
			<>
				<DataModal<JobData>
					ref={ref}
					transformFormData={transformFormData}
					transformInputData={transformInputData}
					entityType="job"
					size={size}
					tabs={tabs}
				/>
				<CompanyModal ref={companyModalRef} />
				<PersonModal ref={personModalRef} />
				<AggregatorModal ref={aggregatorModalRef} />
				<KeywordModal ref={keywordModalRef} />
			</>
		);
	}
);
