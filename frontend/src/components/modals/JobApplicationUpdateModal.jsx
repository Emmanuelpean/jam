import React, { useMemo } from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields, useFormOptions } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { formatDateTime } from "../../utils/TimeUtils.ts";

export const JobApplicationUpdateModal = ({
	show,
	onHide,
	data,
	id,
	onSuccess,
	onDelete,
	endpoint = "jobapplicationupdates",
	submode = "view",
	size = "md",
	jobApplicationId,
}) => {
	const { jobApplications, openJobApplicationModal } = useFormOptions(["jobApplications"]);

	const initialData = useMemo(() => {
		if (submode === "add" && !data?.id) {
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
		formFields.note(),
	];

	const viewFieldsArray = [
		[
			...(jobApplicationId ? [] : [viewFields.jobApplication({ label: "Job Application" })]),
			viewFields.datetime(),
			viewFields.updateType(),
		],
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
				itemName="Update"
				size={size}
				data={initialData}
				id={id}
				fields={fields}
				endpoint={endpoint}
				onSuccess={onSuccess}
				onDelete={onDelete}
				transformFormData={transformFormData}
			/>
		</>
	);
};
