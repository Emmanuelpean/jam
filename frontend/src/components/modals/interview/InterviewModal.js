import React from "react";
import GenericModal from "../GenericModal";
import { formFields, useFormOptions } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";

export const InterviewModal = ({
	show,
	onHide,
	data,
	onSuccess,
	onDelete,
	endpoint = "interviews",
	submode = "view",
	size = "lg",
	jobApplicationId,
}) => {
	const {
		locations,
		persons,
		jobApplications,
		openLocationModal,
		openPersonModal,
		openJobApplicationModal,
		renderLocationModal,
		renderPersonModal,
	} = useFormOptions();

	const formFieldsArray = [
		formFields.jobApplication(jobApplications, openJobApplicationModal),
		[
			formFields.datetime({
				required: true,
			}),
			formFields.interviewType(),
		],
		formFields.location(locations, openLocationModal),
		formFields.interviewers(persons, openPersonModal),
		formFields.note({
			placeholder: "Add notes about the interview, questions asked, impressions, etc...",
		}),
	];

	const viewFieldsArray = [
		viewFields.jobApplication({ label: "Job Application" }),
		[viewFields.date(), viewFields.type()],
		[viewFields.location(), viewFields.interviewers()],
		viewFields.note(),
	];

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const transformFormData = (data) => {
		const transformed = {};

		transformed.date = new Date(data.date).toISOString();
		transformed.type = data.type;
		transformed.location_id = data.location_id;
		transformed.jobapplication_id = data.jobapplication_id;
		transformed.interviewers = data.interviewers;
		transformed.note = data.note || null;

		// // Add jobapplication_id for new interviews if passed as prop
		// if (submode === "add" && jobApplicationId) {
		// 	transformed.jobapplication_id = jobApplicationId;
		// }
		return transformed;
	};

	return (
		<>
			<GenericModal
				show={show}
				onHide={onHide}
				mode="formview"
				submode={submode}
				title="Interview"
				size={size}
				data={data || {}}
				fields={fields}
				endpoint={endpoint}
				onSuccess={onSuccess}
				onDelete={onDelete}
				transformFormData={transformFormData}
			/>

			{renderLocationModal()}

			{renderPersonModal()}
		</>
	);
};

export const InterviewFormModal = (props) => {
	const submode = props.isEdit || props.interview?.id ? "edit" : "add";
	return <InterviewModal {...props} submode={submode} />;
};

export const InterviewViewModal = (props) => <InterviewModal {...props} interview={props.item} submode="view" />;
