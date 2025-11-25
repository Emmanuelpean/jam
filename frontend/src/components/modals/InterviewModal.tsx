import React from "react";
import DataModal, { DataModalProps } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { InterviewDataTransform, JobData } from "../../services/Schemas";
import { useFormOptions } from "../rendering/form/FormOptions";

export interface InterviewModalProps extends DataModalProps {
	jobId?: number;
}

export const InterviewModal: React.FC<InterviewModalProps> = ({
	show,
	onHide,
	data,
	submode = "view",
	size = "lg",
	jobId,
}) => {
	const { locations, persons, jobs, openLocationModal, openPersonModal, renderLocationModal, renderPersonModal } =
		useFormOptions();

	const formFieldsArray = [
		...(!jobId ? [formFields.job(jobs)] : []),
		[
			formFields.datetime({
				required: true,
			}),
			formFields.interviewType(),
		],
		[
			formFields.interviewAttendanceType(),
			formFields.location(locations, openLocationModal, null, {
				displayCondition: (formData: JobData): boolean => {
					return formData.attendance_type === "on-site";
				},
			}),
		],
		formFields.interviewers(persons, openPersonModal),
		formFields.note({
			placeholder: "Add notes about the interview, questions asked, impressions, etc...",
		}),
	];

	const viewFieldsArray = [
		...(!jobId ? [modalViewFields.jobBadge()] : []),
		[modalViewFields.datetime(), modalViewFields.interviewType()],
		[modalViewFields.locationBadge(), modalViewFields.interviewerBadges()],
		modalViewFields.note(),
	];

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const transformFormData = (data: InterviewDataTransform): InterviewDataTransform => {
		return {
			date: new Date(data.date),
			type: data.type,
			location_id: data.location_id,
			job_id: jobId || data.job_id,
			attendance_type: data.attendance_type,
			interviewers: data.interviewers || [],
			note: data.note?.trim() || null,
		};
	};

	return (
		<>
			<DataModal
				show={show}
				onHide={onHide}
				mode={submode}
				itemName="Interview"
				size={size}
				data={data}
				fields={fields}
				endpoint="interviews"
				transformFormData={transformFormData}
			/>

			{renderLocationModal()}
			{renderPersonModal()}
		</>
	);
};
