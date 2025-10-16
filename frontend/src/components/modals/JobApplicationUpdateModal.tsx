import React from "react";
import DataModal, { DataModalProps } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { JobApplicationUpdateData, JobApplicationUpdateDataTransform } from "../../services/Schemas";
import { useFormOptions } from "../rendering/form/FormOptions";

export interface JobApplicationUpdateModalProps extends DataModalProps {
	jobId?: number;
}

export const JobApplicationUpdateModal: React.FC<JobApplicationUpdateModalProps> = ({
	show,
	onHide,
	data,
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
		...(jobId ? [] : [modalViewFields.jobBadge()]),
		[modalViewFields.datetime(), modalViewFields.updateType()],
		modalViewFields.note(),
	];

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const transformFormData = (data: JobApplicationUpdateData): JobApplicationUpdateDataTransform => {
		return {
			date: new Date(data.date),
			type: data.type,
			job_id: jobId || data.job_id,
			note: data.note?.trim() || null,
		};
	};

	return (
		<>
			<DataModal
				show={show}
				onHide={onHide}
				mode={submode}
				itemName="Update"
				size={size}
				data={data}
				fields={fields}
				endpoint="jobapplicationupdates"
				transformFormData={transformFormData}
			/>
		</>
	);
};
