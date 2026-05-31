import React, { forwardRef, useRef } from "react";
import DataModal, { DataModalHandle, Fields, JamDataModalProps } from "./DataModal";
import { useFormFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { useFormOptions } from "../rendering/form/FormOptions";
import { PersonModal } from "./PersonModal";
import { EnrichedInterviewData, InterviewDataTransform } from "../../services/schemas/DataTables";

export interface InterviewModalProps extends JamDataModalProps {
	jobId?: number;
}
export const InterviewModal = forwardRef<DataModalHandle<EnrichedInterviewData>, InterviewModalProps>(
	({ size = "lg", jobId }: InterviewModalProps, ref): JSX.Element => {
		const personModalRef = useRef<DataModalHandle>(null);
		const { persons, jobs, getPersonPreviewConfig } = useFormOptions();
		const ff = useFormFields();

		const formFieldsArray: Fields = [
			...(!jobId ? [ff.jobField(jobs)] : []),
			[
				ff.datetimeField({
					required: true,
				}),
				ff.interviewTypeField(),
			],
			[ff.interviewAttendanceTypeField(), ff.locationField()],
			ff.interviewersField(persons, personModalRef, null, getPersonPreviewConfig),
			ff.noteField({
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
				<DataModal<EnrichedInterviewData>
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
