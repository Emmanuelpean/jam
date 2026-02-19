import React, { forwardRef, JSX, ReactNode, useRef } from "react";
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
import { findClosestOption, findExactOption, useFormOptions } from "../rendering/form/FormOptions";
import { getApplicationStatusBadgeClass } from "../rendering/view/Icons";
import { useAuth } from "../../contexts/AuthContext";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { CompanyModal } from "./CompanyModal";
import { PersonModal } from "./PersonModal";
import { AggregatorModal } from "./AggregatorModal";
import { KeywordModal } from "./KeywordModal";
import { LocationModal } from "./LocationModal";
import { EnrichedJobData, JobData, JobDataTransform, LocationDataTransform } from "../../services/schemas/DataTables";
import { convertToEndOfDay } from "../../utils/TimeUtils";

export const ExtensionJobModal = forwardRef<DataModalHandle, JamDataModalProps>(
	({ size = "xl" }: JamDataModalProps, ref): JSX.Element => {
		const locationModalRef = useRef<DataModalHandle>(null);
		const personModalRef = useRef<DataModalHandle>(null);
		const companyModalRef = useRef<DataModalHandle>(null);
		const aggregatorModalRef = useRef<DataModalHandle>(null);
		const keywordModalRef = useRef<DataModalHandle>(null);
		const { currentUser } = useAuth();
		const dataContext: DataContextValue = useDataContext();
		const { companies, locations, keywords, persons, aggregators } = useFormOptions();

		// Map scraped text fields to JAM IDs and add hint fields expected by
		// scrapedCompany / scrapedLocation form helpers.
		const transformInputData = (data: any) => {
			if (!data) return data;
			const locationStr = [data.location_city, data.location_country].filter(Boolean).join(", ");
			return {
				...data,
				// secondaryName values read by the scraped field helpers
				company: data.company_name || null,
				parsed_location: locationStr || null,
				// pre-select closest matches
				company_id: data.company_name ? findClosestOption(companies, data.company_name) : null,
				location_id: locationStr ? findClosestOption(locations, locationStr) : null,
				source_aggregator_id: findExactOption(aggregators, "LinkedIn"),
				source_type: data.source_type || "aggregator",
			};
		};

		const jobFormFields: Fields = [
			{
				type: "section",
				key: "basic-info",
				title: "Basic Information",
				icon: "bi-briefcase",
				fields: [
					formFields.jobTitle({ placeholder: "Python Software Engineer" }),
					[
						formFields.scrapedCompany(companies, companyModalRef, (d: any) => ({ name: d.company_name || d.company })),
						formFields.url({ label: "Job URL", placeholder: "https://linkedin.com/jobs/123456" }),
					],
				],
			} as SectionConfig,
			{
				type: "section",
				key: "location",
				title: "Location",
				icon: "bi-geo-alt",
				fields: [
					formFields.scrapedLocation(
						locations,
						locationModalRef,
						(d: any): LocationDataTransform => ({
							city: d.location_city ?? null,
							country: d.location_country ?? null,
							postcode: null,
						})
					),
					formFields.attendanceType(),
				],
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
							displayCondition: (formData: JobDataTransform): boolean =>
								["aggregator", "aggregator_email"].includes(formData.source_type || ""),
						}),
						formFields.recruiter(persons, personModalRef, null, null, {
							displayCondition: (formData: JobDataTransform): boolean =>
								formData.source_type === "recruiter",
						}),
						formFields.company(companies, companyModalRef, null, null, {
							name: "recruitment_company_id",
							displayCondition: (formData: JobDataTransform): boolean =>
								formData.source_type === "recruitment_company",
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
					modalViewFields.description(),
					formFields.note({ placeholder: "Add any additional notes about this role..." }),
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
							displayCondition: (formData: JobDataTransform): boolean =>
								formData.applied_via ? formData.applied_via === "aggregator" : true,
						}),
					],
					formFields.applicationUrl({ placeholder: "https://linkedin.com/jobs/123456/apply" }),
				],
			} as SectionConfig,
			{
				type: "section",
				key: "application-notes",
				title: "Notes",
				icon: "bi-journal-text",
				fields: [
					formFields.note({
						placeholder: "Notes about the application process...",
						name: "application_note",
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
		});

		const customValidation = async (formData: JobData): Promise<ValidationErrors> => {
			const errors: ValidationErrors = {};
			if (formData.salary_min && isNaN(Number(formData.salary_min)))
				errors.salary_min = "Minimum salary must be a valid number";
			if (formData.salary_max && isNaN(Number(formData.salary_max)))
				errors.salary_max = "Maximum salary must be a valid number";
			if (formData.url) {
				const dup = dataContext.jobs.find(
					(j: EnrichedJobData) =>
						j.url?.trim().toLowerCase() === formData.url?.trim().toLowerCase() && j.id !== formData.id
				);
				if (dup) errors.url = "A job with this URL already exists";
			}
			return errors;
		};

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
				<DataModal
					ref={ref}
					transformFormData={transformFormData}
					transformInputData={transformInputData}
					entityType="job"
					size={size}
					tabs={tabs}
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
