import React, { useMemo } from "react";
import GenericModal from "./GenericModal";
import { formFields, useFormOptions } from "../rendering/FormRenders";
import { viewFields } from "../rendering/ViewRenders";
import { formatDateTime } from "../../utils/TimeUtils";

export const InterviewModal = ({
	show,
	onHide,
	data,
	onSuccess,
	onDelete,
	endpoint = "jobapplicationupdates",
	submode = "view",
	size = "lg",
	jobApplicationId,
}) => {
	const { jobApplications, openJobApplicationModal } = useFormOptions();

	const initialData = useMemo(() => {
		if (submode === "add" && !data) {
			return { date: formatDateTime() };
		}
		return data || {};
	}, [data, submode]);

	const formFieldsArray = [
		...(!jobApplicationId ? [formFields.jobApplication(jobApplications, openJobApplicationModal)] : []),
		[
			formFields.datetime({
				required: true,
			}),
			formFields.updateType(),
		],
		formFields.note({
			placeholder: "Add notes about the interview, questions asked, impressions, etc...",
		}),
	];

	const viewFieldsArray = [
		...(!jobApplicationId ? [viewFields.jobApplication({ label: "Job Application" })] : []),
		[viewFields.datetime(), viewFields.updateType()],
		viewFields.note(),
	];

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const transformFormData = (data) => {
		return {
			date: new Date(data.date).toISOString(),
			type: data.type,
			job_application_id: jobApplicationId || data.job_application_id,
			note: data.note?.trim() || null,
		};
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
				data={initialData}
				fields={fields}
				endpoint={endpoint}
				onSuccess={onSuccess}
				onDelete={onDelete}
				transformFormData={transformFormData}
			/>
		</>
	);
};

export const JobApplicationUpdateFormModal = (props) => {
	const submode = props.isEdit || props.interview?.id ? "edit" : "add";
	return <InterviewModal {...props} submode={submode} />;
};

export const JobApplicationUpdateViewModal = (props) => (
	<InterviewModal {...props} interview={props.item} submode="view" />
);
