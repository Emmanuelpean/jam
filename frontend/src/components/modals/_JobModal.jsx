import React from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields, useFormOptions } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ViewRenders";

export const JobModal = ({
	show,
	onHide,
	data,
	onSuccess,
	onDelete,
	endpoint = "jobs",
	submode = "view",
	size = "lg",
}) => {
	// Use the enhanced hook to get form options data and modal management
	const {
		companies,
		locations,
		keywords,
		persons,
		openCompanyModal,
		openLocationModal,
		openKeywordModal,
		openPersonModal,
		renderCompanyModal,
		renderLocationModal,
		renderKeywordModal,
		renderPersonModal,
	} = useFormOptions(["companies", "locations", "keywords", "persons", "jobApplications"]);

	const formFieldsArray = [
		formFields.jobTitle(),
		[formFields.company(companies, openCompanyModal), formFields.location(locations, openLocationModal)],
		[formFields.keywords(keywords, openKeywordModal), formFields.contacts(persons, openPersonModal)],
		formFields.url({ label: "Job URL" }),
		[formFields.salaryMin(), formFields.salaryMax()],
		formFields.personalRating(),
		formFields.description(),
		formFields.note(),
	];

	const viewFieldsArray = [
		[viewFields.title(), viewFields.company()],
		[viewFields.location(), viewFields.jobApplication()],
		viewFields.description(),
		[viewFields.salaryRange(), viewFields.personalRating()],
		viewFields.url({ label: "Job URL" }),
		[viewFields.keywords(), viewFields.persons()],
	];

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const transformFormData = (data) => {
		return {
			title: data.title.trim(),
			description: data.description?.trim() || null,
			note: data.note?.trim() || null,
			url: data.url?.trim() || null,
			salary_min: data.salary_min || null,
			salary_max: data.salary_max || null,
			personal_rating: data.personal_rating || null,
			company_id: data.company_id || null,
			location_id: data.location_id || null,
			keywords: data.keywords?.map((item) => item.id || item) || [],
			contacts: data.contacts?.map((item) => item.id || item) || [],
		};
	};

	return (
		<>
			<GenericModal
				show={show}
				onHide={onHide}
				mode="formview"
				submode={submode}
				title="Job"
				size={size}
				data={data || {}}
				fields={fields}
				endpoint={endpoint}
				onSuccess={onSuccess}
				onDelete={onDelete}
				transformFormData={transformFormData}
			/>

			{renderCompanyModal()}
			{renderLocationModal()}
			{renderKeywordModal()}
			{renderPersonModal()}
		</>
	);
};

export const JobFormModal = (props) => {
	const submode = props.isEdit || props.job?.id ? "edit" : "add";
	return <JobModal {...props} submode={submode} />;
};

export const JobViewModal = (props) => <JobModal {...props} submode="view" />;
