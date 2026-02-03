import React, { forwardRef, JSX, useRef } from "react";
import DataModal, {
	DataModalHandle,
	Fields,
	JamDataModalProps,
	ValidationErrors,
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
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { EnrichedJobData, JobData } from "../../services/schemas/DataTables";
import { ScrapedJobData, ScrapedJobUpdate } from "../../services/schemas/Services";
import { useConfig } from "../../contexts/ConfigContext";

export const ScrapedJobModal = forwardRef<DataModalHandle, JamDataModalProps>(
	({ size = "xl", onSuccess, onDelete, canEdit = true }: JamDataModalProps, ref): JSX.Element => {
		const dataContext: DataContextValue = useDataContext();
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
				location_id: data.location ? findClosestOption(locations, data.location) : null,
				aggregator_id: data.platform ? findExactOption(aggregators, data.platform) : null,
			};
		};

		const jobFormFields: Fields = [
			modalViewFields.jobRating(),
			formFields.jobTitle({ placeholder: "Python Software Engineer" }),
			formFields.description({
				placeholder: "",
				autoHeight: true,
			}),
			[
				formFields.scrapedCompany(companies, companyModalRef, (scrapedJob: ScrapedJobData) => ({
					name: scrapedJob.company,
				})),
				formFields.url({
					label: "Job URL",
					placeholder: "https://linkedin.com/jobs/453635",
					required: true,
				}),
			],
			[
				formFields.scrapedLocation(locations, locationModalRef, (scrapedJob: ScrapedJobData) => ({
					postcode: scrapedJob.location_postcode,
					city: scrapedJob.location_city,
					country: scrapedJob.location_country,
				})),
				formFields.attendanceType(),
			],
			[formFields.keywords(keywords, keywordModalRef), formFields.contacts(persons, personModalRef)],
			[formFields.salaryMin({ placeholder: "35000" }), formFields.salaryMax({ placeholder: "45000" })],
			[
				formFields.personalRating(),
				formFields.deadline(),
				formFields.aggregator(aggregators, aggregatorModalRef, (scrapedJob: ScrapedJobData) => ({
					name: scrapedJob.platform ? capitalise(scrapedJob.platform) : undefined,
				})),
			],
			formFields.note({
				placeholder:
					"This role offers a chance to apply Python expertise to build scalable solutions " +
					"while exploring opportunities for growth in automation, data analysis, and collaborative software development.",
			}),
			modalViewFields.scrapedLocationMap(),
		];

		const viewFields: Fields = [
			modalViewFields.title({ isTitle: true }),
			modalViewFields.description(),
			[modalViewFields.company(), modalViewFields.location()],
			[modalViewFields.platform(), modalViewFields.url()],
			modalViewFields.scrapedLocationMap(),
		];

		const customValidation = async (formData: JobData): Promise<ValidationErrors> => {
			const errors: ValidationErrors = {};
			const duplicates: EnrichedJobData[] = dataContext.jobs.filter(
				(job: EnrichedJobData): boolean =>
					job.url?.trim().toLowerCase() === formData.url?.trim().toLowerCase() && job.id !== formData?.id
			);
			if (duplicates.length > 0) {
				errors.name = `A Job with this URL already exists`;
			}
			return errors;
		};

		const warningMessage = (data: ScrapedJobData) => {
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

			if (data?.is_failed) {
				const reportLink = createReportLink("Scraped Job Error Report", data?.scrape_error);
				result.push({
					key: "inactive",
					message: (
						<>
							This job could not be scraped properly due to an error.
							{reportLink && <> You can {reportLink}.</>}
						</>
					),
					variant: "warning",
				});
			}

			if (data?.job_rating?.is_success === false) {
				const reportLink = createReportLink("Job Rating Error Report", data?.job_rating?.error);
				result.push({
					key: "no_rating",
					message: (
						<>
							This job could not be rated automatically due to an error.
							{reportLink && <> You can {reportLink}.</>}
						</>
					),
					variant: "warning",
				});
			}

			if (data?.job_rating?.is_skipped) {
				result.push({
					key: "skipped",
					message: "This job was not scraped as you have exhausted your monthly quota.",
					variant: "info",
				});
			}

			return result.length ? result : null;
		};

		const transformData = (_scrapedJob: ScrapedJobData): ScrapedJobUpdate => {
			return { is_imported: true };
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
					validation={customValidation}
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
