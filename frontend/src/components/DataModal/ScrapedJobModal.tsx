import React, { forwardRef, JSX, useRef } from "react";
import DataModal, {
	DataModalHandle,
	Fields,
	JamDataModalProps,
	SectionConfig,
	WarningMessageConfig,
} from "./DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { findClosestOption, findExactOption, useFormOptions } from "../rendering/form/FormOptions";
import { modalViewFields } from "../rendering/view/ModalFields";
import { capitalise } from "../../utils/StringUtils";
import { CompanyModal } from "./CompanyModal";
import { LocationModal } from "./LocationModal";
import { KeywordModal } from "./KeywordModal";
import { PersonModal } from "./PersonModal";
import { AggregatorModal } from "./AggregatorModal";
import { JamData, useDataContext } from "../../contexts/DataContext";
import { JobData, JobDataTransform, LocationDataTransform } from "../../services/schemas/DataTables";
import { ScrapedJobData, ScrapedJobUpdate } from "../../services/schemas/Services";
import { useConfig } from "../../contexts/ConfigContext";
import { convertToEndOfDay } from "../../utils/TimeUtils";
import { ApiResponse } from "../../services/api/Base";

export const ScrapedJobModal = forwardRef<DataModalHandle, JamDataModalProps>(
	({ size = "xl", onDelete, onSuccess: parentOnSuccess, canEdit = true }: JamDataModalProps, ref): JSX.Element => {
		const { addEntity } = useDataContext();
		const { config } = useConfig();
		const companyModalRef = useRef<DataModalHandle>(null);
		const locationModalRef = useRef<DataModalHandle>(null);
		const keywordModalRef = useRef<DataModalHandle>(null);
		const personModalRef = useRef<DataModalHandle>(null);
		const aggregatorModalRef = useRef<DataModalHandle>(null);
		const { companies, locations, keywords, persons, aggregators } = useFormOptions();

		const transformInputData = (data: ScrapedJobData) => {
			if (!data) return data;
			return {
				...data,
				company_id: data.company ? findClosestOption(companies, data.company) : null,
				location_id: data.parsed_location ? findClosestOption(locations, data.parsed_location) : null,
				source_aggregator_id: data.platform ? findExactOption(aggregators, data.platform) : null,
				source_type: "aggregator_email",
			};
		};

		const jobFormFields: Fields = [
			{
				type: "section",
				key: "rating",
				title: "AI Rating",
				icon: "bi-stars",
				fields: [modalViewFields.jobRatingSection()],
				displayCondition: (data: any): boolean =>
					!(data?.is_closed || (data?.deadline != null && data.deadline < new Date())),
			} as SectionConfig,

			{
				type: "section",
				key: "basic-info",
				title: "Basic Information",
				icon: "bi-briefcase",
				fields: [
					modalViewFields.title({ isTitle: true }),
					[
						formFields.scrapedCompany(companies, companyModalRef, (scrapedJob: ScrapedJobData) => ({
							name: scrapedJob.company,
						})),
						formFields.jobURl(),
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
						(scrapedJob: ScrapedJobData): LocationDataTransform => ({
							postcode: scrapedJob.location_postcode,
							city: scrapedJob.location_city,
							country: scrapedJob.location_country,
						})
					),
					formFields.attendanceType(),
					modalViewFields.scrapedLocationMap(),
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
						formFields.aggregator(
							aggregators,
							aggregatorModalRef,
							(scrapedJob: ScrapedJobData) => ({
								name: scrapedJob.platform ? capitalise(scrapedJob.platform) : undefined,
							}),
							null,
							{
								name: "source_aggregator_id",
								displayCondition: (formData: JobDataTransform): boolean => {
									return ["aggregator", "aggregator_email"].includes(
										formData.source_type ? formData.source_type : ""
									);
								},
							}
						),
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
					modalViewFields.description(),
					formFields.note({
						placeholder:
							"This role offers a chance to apply Python expertise to build scalable solutions " +
							"while exploring opportunities for growth in automation, data analysis, and collaborative software development.",
					}),
				],
			} as SectionConfig,
			{
				type: "section",
				key: "emails",
				title: "Job Alert Emails",
				icon: "bi-envelope-open",
				defaultExpanded: true,
				fields: [modalViewFields.scrapedJobEmails()],
			} as SectionConfig,
		];

		const viewFields: Fields = [
			modalViewFields.jobRatingSection(),
			modalViewFields.title({ isTitle: true }),
			modalViewFields.description(),
			[modalViewFields.company(), modalViewFields.location()],
			[modalViewFields.platform(), modalViewFields.url()],
			modalViewFields.scrapedLocationMap(),
		];

		const warningMessage = (data: ScrapedJobData): WarningMessageConfig[] | null => {
			const result: WarningMessageConfig[] = [];

			const createReportLink = (subject: string, errorMessage: string | null): JSX.Element | null => {
				const supportEmail: string = config?.support_email;
				if (!supportEmail) return null;

				const body: string = encodeURIComponent(
					`Error Details:\n${errorMessage || "Unknown error"}\n\nJob ID: ${data?.id || "N/A"}\nJob Title: ${data?.title || "N/A"}\nJob URL: ${data?.url || "N/A"}`
				);
				const mailtoLink = `mailto:${supportEmail}?subject=${encodeURIComponent(subject)}&body=${body}`;

				return (
					<a href={mailtoLink} style={{ color: "inherit", textDecoration: "underline" }}>
						report it here
					</a>
				);
			};

			// Scraped Job Status
			if (!data?.is_processed && !data?.scrape_error.length) {
				result.push({
					key: "scraping_not_processed",
					message: "This job has yet to be processed. Please come back soon.",
				});
			}
			if (!data?.is_processed && data?.scrape_error.length) {
				result.push({
					key: "scraping_retry_pending",
					message: `Scraping failed (attempt ${data.retry_count}/3). It will be reattempted soon.`,
					variant: "warning",
				});
			}
			if (data?.is_failed) {
				const reportLink = createReportLink(
					"Scraped Job Error Report",
					data?.scrape_error.map((e) => e.error).join("\n\n---\n\n") || null
				);
				result.push({
					key: "scraping_failed",
					message: (
						<>
							This job could not be scraped properly due to an unexpected error.
							{reportLink && <> You can {reportLink}.</>}
						</>
					),
					variant: "warning",
				});
			}
			if (data?.is_skipped) {
				result.push({
					key: "scraping_skipped",
					message: "This job was not scraped due to the following reason: " + data?.skip_reason,
				});
			}
			if (data?.is_closed || (data?.deadline != null && data.deadline < new Date())) {
				result.push({
					key: "job_closed",
					message: "This job is now closed and you may not be able to apply to it.",
					variant: "warning",
				});
			}

			return result.length ? result : null;
		};

		const transformData = (_scrapedJob: ScrapedJobData): ScrapedJobUpdate => {
			return { is_imported: true };
		};

		const onSuccess = async (formData: JobData): Promise<any> => {
			const jobData: Partial<JobDataTransform> = {
				title: formData.title.trim(),
				description: formData.description?.trim() || null,
				note: formData.note?.trim() || null,
				url: formData.url?.trim() || null,
				salary_min: formData.salary_min || null,
				salary_max: formData.salary_max || null,
				salary_currency: formData.salary_currency || null,
				personal_rating: formData.personal_rating || null,
				company_id: formData.company_id || null,
				location_id: formData.location_id || null,
				source_type: formData.source_type || null,
				source_aggregator_id: formData.source_aggregator_id || null,
				recruiter_id: formData.recruiter_id || null,
				recruitment_company_id: formData.recruitment_company_id || null,
				deadline: formData.deadline ? convertToEndOfDay(formData.deadline) : null,
				keywords: formData.keywords || [],
				contacts: formData.contacts || [],
				attendance_type: formData.attendance_type?.trim() || null,
			};
			const result: ApiResponse<JamData> = await addEntity("job", jobData);
			parentOnSuccess?.(result);
		};

		return (
			<>
				<DataModal
					ref={ref}
					fields={{ form: jobFormFields, view: viewFields }}
					transformFormData={transformData}
					transformInputData={transformInputData}
					entityType="scrapedJob"
					size={size}
					onSuccess={onSuccess}
					onDelete={onDelete}
					warningMessage={warningMessage}
					canEdit={canEdit}
				/>
				<CompanyModal ref={companyModalRef} />
				<LocationModal ref={locationModalRef} />
				<KeywordModal ref={keywordModalRef} />
				<PersonModal ref={personModalRef} />
				<AggregatorModal ref={aggregatorModalRef} />
			</>
		);
	}
);
