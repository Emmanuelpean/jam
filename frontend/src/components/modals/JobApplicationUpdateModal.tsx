import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, JamDataModalProps, Fields } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { JobApplicationUpdateData, JobApplicationUpdateDataTransform } from "../../services/Schemas";
import { useFormOptions } from "../rendering/form/FormOptions";

export interface JobApplicationUpdateModalProps extends JamDataModalProps {
	jobId?: number;
}

export const JobApplicationUpdateModal = forwardRef<DataModalHandle, JobApplicationUpdateModalProps>(
	({ size = "lg", jobId }: JobApplicationUpdateModalProps, ref): JSX.Element => {
		const { jobs } = useFormOptions();

		const formFieldsArray: Fields = [
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

		const viewFieldsArray: Fields = [
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
	},
);
