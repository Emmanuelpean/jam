import React, { forwardRef } from "react";
import DataModal, { DataModalHandle, DataModalProps, GenericModalProps } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { JobApplicationUpdateData, JobApplicationUpdateDataTransform } from "../../services/Schemas";
import { useFormOptions } from "../rendering/form/FormOptions";

export interface JobApplicationUpdateModalProps extends DataModalProps {
	jobId?: number;
}

export const JobApplicationUpdateModal = forwardRef<
	DataModalHandle,
	Omit<GenericModalProps, "endpoint" | "fields" | "transformFormData"> & { jobId?: number }
>(({ size = "lg", jobId }, ref) => {
	const { jobs } = useFormOptions();

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
				ref={ref}
				itemName="Update"
				size={size}
				fields={fields}
				endpoint="jobapplicationupdates"
				transformFormData={transformFormData}
			/>
		</>
	);
});
