import React from "react";
import DataModal, { DataModalProps, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { JobData, ScrapedJobData } from "../../services/Schemas";
import { jobsApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { SelectOption, useFormOptions } from "../rendering/form/FormOptions";
import stringSimilarity from "string-similarity";
import { modalViewFields } from "../rendering/view/ModalFields";
import { capitalise } from "../../utils/Utils";

interface JobAndApplicationProps extends DataModalProps {
	data: ScrapedJobData;
}

export const ScrapedJobModal: React.FC<JobAndApplicationProps> = ({
	show,
	onHide,
	data,
	submode,
	size = "xl",
	onSuccess,
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
	} = useFormOptions({
		companies: () => ({ name: data?.company }),
		locations: () => ({
			postcode: data?.location_postcode,
			city: data?.location_city,
			country: data?.location_country,
		}),
		aggregators: () => ({ name: data?.platform ? capitalise(data?.platform) : undefined }),
	});

	function findClosest(options: SelectOption[], name: string): string | null {
		if (!name || options.length === 0) return null;
		const names: string[] = options.map((c: SelectOption): string => c.label);
		const result = stringSimilarity.findBestMatch(name, names);

		// Define a minimum threshold (e.g., 0.3 or 0.4)
		const MIN_SIMILARITY_THRESHOLD = 0.4;

		if (result.bestMatch.rating < MIN_SIMILARITY_THRESHOLD) {
			return null;
		}

		return options[result.bestMatchIndex]?.value || null;
	}

	function findExact(options: SelectOption[], name: string): string | null | undefined {
		if (!name || options.length === 0) return null;
		const match: SelectOption | undefined = options.find(
			(opt: SelectOption): boolean => opt.label.toLowerCase() === name.toLowerCase(),
		);
		return match ? match.value : null;
	}

	const patchedData = React.useMemo(() => {
		if (!data) return data;
		return {
			...data,
			company_id: data.company ? findClosest(companies, data.company) : null,
			location_id: data.location ? findClosest(locations, data.location) : null,
			aggregator_id: data.platform ? findExact(aggregators, data.platform) : null,
		};
	}, [data, companies, locations]);

	const jobFormFields = [
		formFields.jobTitle({ placeholder: "Python Software Engineer" }),
		formFields.description({
			placeholder: "",
		}),
		[
			formFields.scrapedCompany(companies, openCompanyModal),
			formFields.url({ label: "Job URL", placeholder: "https://linkedin.com/jobs/453635", required: true }),
		],
		[formFields.scrapedLocation(locations, openLocationModal), formFields.attendanceType()],
		[formFields.keywords(keywords, openKeywordModal), formFields.contacts(persons, openPersonModal)],
		[formFields.salaryMin({ placeholder: "35000" }), formFields.salaryMax({ placeholder: "45000" })],
		[formFields.personalRating(), formFields.deadline(), formFields.aggregator(aggregators, openAggregatorModal)],

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
				show={show}
				onHide={onHide}
				data={patchedData}
				mode={submode}
				fields={{ form: jobFormFields, view: [] }}
				transformFormData={transformData}
				itemName="Scraped Job"
				endpoint="scraped_jobs"
				size={size}
				validation={customValidation}
				onSuccess={onSuccess}
				warningMessage={warningMessage}
			/>

			{renderCompanyModal()}
			{renderLocationModal()}
			{renderKeywordModal()}
			{renderPersonModal()}
			{renderAggregatorModal()}
		</>
	);
};
