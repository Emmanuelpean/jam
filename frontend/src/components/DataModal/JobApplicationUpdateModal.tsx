import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, Fields, JamDataModalProps } from "./DataModal";
import { useFormFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { useFormOptions } from "../rendering/form/FormOptions";
import {
	EnrichedJobApplicationUpdateData,
	JobApplicationUpdateData,
	JobApplicationUpdateDataTransform,
} from "../../services/schemas/DataTables";

export interface JobApplicationUpdateModalProps extends JamDataModalProps {
	jobId?: number;
}

export const JobApplicationUpdateModal = forwardRef<
	DataModalHandle<EnrichedJobApplicationUpdateData>,
	JobApplicationUpdateModalProps
>(({ size = "lg", jobId }: JobApplicationUpdateModalProps, ref): JSX.Element => {
	const { jobs } = useFormOptions();
	const ff = useFormFields();

	const formFieldsArray: Fields = [
		...(!jobId ? [ff.jobField(jobs)] : []),
		[
			ff.datetimeField({
				required: true,
			}),
			ff.updateTypeField(),
		],
		ff.noteField({
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
			date: data.date,
			type: data.type,
			job_id: jobId || data.job_id,
			note: data.note?.trim() || null,
		};
	};

	return (
		<>
			<DataModal<EnrichedJobApplicationUpdateData>
				ref={ref}
				size={size}
				fields={fields}
				entityType="jobApplicationUpdate"
				transformFormData={transformFormData}
			/>
		</>
	);
});
