import React, { forwardRef, useRef } from "react";
import DataModal, { DataModalHandle, Fields, JamDataModalProps } from "./DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { useFormOptions } from "../rendering/form/FormOptions";
import { PersonModal } from "./PersonModal";
import { InterviewData, InterviewDataTransform, JobData } from "../../services/schemas/DataTables";

export interface InterviewModalProps extends JamDataModalProps {
	jobId?: number;
}
export const InterviewModal = forwardRef<DataModalHandle<InterviewData>, InterviewModalProps>(
	({ size = "lg", jobId }: InterviewModalProps, ref): JSX.Element => {
		const personModalRef = useRef<DataModalHandle>(null);
		const { persons, jobs, getPersonPreviewConfig } = useFormOptions();

		const formFieldsArray: Fields = [
			...(!jobId ? [formFields.job(jobs)] : []),
			[
				formFields.datetime({
					required: true,
				}),
				formFields.interviewType(),
			],
			[formFields.interviewAttendanceType(), formFields.location()],
			formFields.interviewers(persons, personModalRef, null, getPersonPreviewConfig),
			formFields.note({
				placeholder: "Add notes about the interview, questions asked, impressions, etc...",
			}),
		];

		const viewFieldsArray: Fields = [
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
				date: data.date,
				type: data.type,
				location: data.location?.trim() || null,
				job_id: jobId || data.job_id,
				attendance_type: data.attendance_type,
				interviewers: data.interviewers || [],
				note: data.note?.trim() || null,
			};
		};

		return (
			<>
				<DataModal<InterviewData>
					ref={ref}
					size={size}
					fields={fields}
					entityType="interview"
					transformFormData={transformFormData}
				/>

				<PersonModal ref={personModalRef} />
			</>
		);
	}
);
