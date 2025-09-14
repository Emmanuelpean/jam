import React from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields, useFormOptions } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { DataModalProps } from "./AggregatorModal";
import { InterviewData, JobData } from "../../services/Schemas";

interface InterviewModalProps extends DataModalProps {
	jobId?: string | number;
}

export const InterviewModal: React.FC<InterviewModalProps> = ({
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
	const { locations, persons, jobs, openLocationModal, openPersonModal, renderLocationModal, renderPersonModal } =
		useFormOptions(show ? ["locations", "persons", "jobs"] : []);

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
			formFields.location(locations, openLocationModal, {
				condition: (formData: JobData): boolean => {
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
		...(!jobId ? [viewFields.jobBadge()] : []),
		[viewFields.datetime(), viewFields.type()],
		[viewFields.locationBadge(), viewFields.interviewerBadges()],
		viewFields.note(),
	];

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const transformFormData = (data: InterviewData) => {
		return {
			date: new Date(data.date!).toISOString(),
			type: data.type!,
			location_id: data.location_id!,
			job_id: jobId || data.job_id!,
			attendance_type: data.attendance_type!,
			interviewers: data.interviewers?.map((interviewer) => interviewer.id || interviewer) || [],
			note: data.note?.trim() || null,
		};
	};

	return (
		<>
			<GenericModal
				show={show}
				onHide={onHide}
				submode={submode}
				itemName="Interview"
				size={size}
				data={data}
				id={id}
				fields={fields}
				endpoint="interviews"
				onSuccess={onSuccess}
				onDelete={onDelete}
				transformFormData={transformFormData}
			/>

			{renderLocationModal()}
			{renderPersonModal()}
		</>
	);
};
