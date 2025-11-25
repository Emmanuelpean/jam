// noinspection DuplicatedCode

import React from "react";
import DataModal, { DataModalProps, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { JobData, ScrapedJobData } from "../../services/Schemas";
import { jobsApi, scrapedJobApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { SelectOption, useFormOptions } from "../rendering/form/FormOptions";
import stringSimilarity from "string-similarity";
import { modalViewFields } from "../rendering/view/ModalFields";

interface JobAndApplicationProps extends DataModalProps {
	defaultActiveTab?: "job" | "application";
	data: ScrapedJobData;
}

export const ScrapedJobModal: React.FC<JobAndApplicationProps> = ({ show, onHide, data, submode, size = "xl" }) => {
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
		aggregators: () => ({
			name: data?.emails?.[0]?.platform
				? data.emails[0].platform[0].toUpperCase() + data.emails[0].platform.slice(1)
				: undefined,
		}),
	});

	function findClosest(options: SelectOption[], name: string): string | null | undefined {
		if (!name || options.length === 0) return null;
		const names: string[] = options.map((c: SelectOption): string => c.label);
		const { bestMatchIndex } = stringSimilarity.findBestMatch(name, names);
		return options[bestMatchIndex]?.value;
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
			aggregator_id: data.emails[0].platform ? findExact(aggregators, data.emails[0].platform) : null,
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

	const transformData = (jobData: JobData) => {
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
			source_id: jobData.source_id || null,
			deadline: jobData.deadline ? jobData.deadline + "T23:59:59" : null,
			keywords: jobData.keywords || [],
			contacts: jobData.contacts || [],
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

	const handleOnSuccess = (_createdData: any) => {
		if (!token) {
			return;
		}
		scrapedJobApi.update(data.id, { is_imported: true }, token).then((_r) => {});
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
				endpoint="jobs"
				size={size}
				validation={customValidation}
				onSuccess={handleOnSuccess}
			/>

			{renderCompanyModal()}
			{renderLocationModal()}
			{renderKeywordModal()}
			{renderPersonModal()}
			{renderAggregatorModal()}
		</>
	);
};
