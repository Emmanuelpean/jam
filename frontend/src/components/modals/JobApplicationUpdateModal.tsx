import React, { useMemo } from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields, useFormOptions } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { formatDateTime } from "../../utils/TimeUtils";
import { DataModalProps } from "./AggregatorModal";
import { JobApplicationUpdateData } from "../../services/Schemas";

interface JobApplicationUpdateModalProps extends DataModalProps {
	jobApplicationId?: string | number;
}

export const JobApplicationUpdateModal: React.FC<JobApplicationUpdateModalProps> = ({
	show,
	onHide,
	data,
	id,
	onSuccess,
	onDelete,
	submode = "view",
	size = "sm",
	jobApplicationId,
}) => {
	const { jobs } = useFormOptions(["jobs"]);

	const initialData = useMemo(() => {
		if (submode === "add" && !data?.id) {
			return { date: formatDateTime() };
		}
		return data || {};
	}, [data, submode]);

	const formFieldsArray = [
		...(!jobApplicationId ? [formFields.job(jobs)] : []),
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
			...(jobApplicationId ? [] : [viewFields.job({ label: "Job Application" })]),
			viewFields.datetime(),
			viewFields.updateType(),
		],
		viewFields.note(),
	];

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const transformFormData = (data: JobApplicationUpdateData) => {
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
				submode={submode}
				itemName="Update"
				size={size}
				data={initialData}
				id={id}
				fields={fields}
				endpoint="jobapplicationupdates"
				onSuccess={onSuccess}
				onDelete={onDelete}
				transformFormData={transformFormData}
			/>
		</>
	);
};
