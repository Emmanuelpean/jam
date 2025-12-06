import React, { forwardRef, useRef, JSX } from "react";
import DataModal, { DataModalHandle, Fields, GenericModalProps, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { JobData, ScrapedJobData } from "../../services/Schemas";
import { jobsApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { findClosestOption, findExactOption, useFormOptions } from "../rendering/form/FormOptions";
import { modalViewFields } from "../rendering/view/ModalFields";
import { capitalise } from "../../utils/StringUtils";
import { CompanyModal } from "./CompanyModal";
import { LocationModal } from "./LocationModal";
import { KeywordModal } from "./KeywordModal";
import { PersonModal } from "./PersonModal";
import { AggregatorModal } from "./AggregatorModal";

interface ScrapedJobModalProps
	extends Omit<GenericModalProps, "endpoint" | "fields" | "validation" | "transformFormData" | "itemName"> {
	data: ScrapedJobData;
}

export const ScrapedJobModal = forwardRef<DataModalHandle, ScrapedJobModalProps>(
	({ data, size = "xl", onSuccess }, ref): JSX.Element => {
		const { token } = useAuth();
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

		const warningMessage: string | null = data?.is_failed ? "This job could not be scraped properly." : null;

		const transformData = (_scrapedJob: ScrapedJobData) => {
			return { is_imported: true };
		};

		return (
			<>
				<DataModal
					ref={ref}
					fields={{ form: jobFormFields, view: [] }}
					transformFormData={transformData}
					transformInputData={transformInputData}
					itemName="Scraped Job"
					endpoint="scraped_jobs"
					size={size}
					validation={customValidation}
					onSuccess={onSuccess}
					warningMessage={warningMessage}
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
