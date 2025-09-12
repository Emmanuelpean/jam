import React, { useMemo } from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields, useFormOptions } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { formatDateTime } from "../../utils/TimeUtils";
import { DataModalProps } from "./AggregatorModal";
import { JobApplicationUpdateData } from "../../services/Schemas";

interface JobApplicationUpdateModalProps extends DataModalProps {
	jobId?: string | number;
}

export const JobApplicationUpdateModal: React.FC<JobApplicationUpdateModalProps> = ({
	show,
	onHide,
	data,
	id,
	onSuccess,
	onDelete,
	submode = "view",
	size = "lg",
	jobId,
}) => {
	const { jobs } = useFormOptions(show ? ["jobs"] : []);

	const formFieldsArray = [
		...(!jobId ? [formFields.job(jobs)] : []),
		[
			formFields.datetime({
				required: true,
			}),
			formFields.updateType(),
		],
		formFields.note({
			placeholder:
				"Application is under review and the hiring team will contact me regarding the next steps in the process.",
		}),
	];

	const viewFieldsArray = [
		...(jobId ? [] : [viewFields.jobBadge()]),
		[viewFields.datetime(), viewFields.updateType()],
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
			job_id: jobId || data.job_id,
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
				data={data}
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
