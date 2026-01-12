import React, { forwardRef, JSX, useRef } from "react";
import DataModal, {
	DataModalHandle,
	JamDataModalProps,
	Fields,
	ValidationErrors,
	WarningMessageConfig,
} from "./DataModal/DataModal";
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
import { ScrapedJobData } from "../../services/schemas/Services";

export const ScrapedJobModal = forwardRef<DataModalHandle, JamDataModalProps>(
	({ size = "xl", onSuccess, canEdit = true }: JamDataModalProps, ref): JSX.Element => {
		const dataContext: DataContextValue = useDataContext();
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
					job.url?.trim().toLowerCase() === formData.url?.trim().toLowerCase() && job.id !== formData?.id,
			);
			if (duplicates.length > 0) {
				errors.name = `A Job with this URL already exists`;
			}
			return errors;
		};

		const warningMessage = (data: ScrapedJobData) => {
			const result: WarningMessageConfig[] = [];

			if (data?.is_failed) {
				result.push({
					key: "inactive",
					message: "This job could not be scraped properly.",
					variant: "warning",
				});
			}

			if (data?.job_rating?.is_success === false) {
				result.push({
					key: "no_rating",
					message: "This job could not be rated automatically.",
					variant: "warning",
				});
			}

			return result.length ? result : null;
		};

		const transformData = (_scrapedJob: ScrapedJobData) => {
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
	},
);
