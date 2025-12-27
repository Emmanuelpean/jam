import React, { forwardRef, useRef } from "react";
import DataModal, { DataModalHandle, JamDataModalProps, Fields } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { InterviewDataTransform, JobData } from "../../services/Schemas";
import { useFormOptions } from "../rendering/form/FormOptions";
import { LocationModal } from "./LocationModal";
import { PersonModal } from "./PersonModal";

export interface InterviewModalProps extends JamDataModalProps {
	jobId?: number;
}
export const InterviewModal = forwardRef<DataModalHandle, InterviewModalProps>(
	({ size = "lg", jobId }: InterviewModalProps, ref) => {
		const locationModalRef = useRef<DataModalHandle>(null);
		const personModalRef = useRef<DataModalHandle>(null);
		const { locations, persons, jobs } = useFormOptions();

		const formFieldsArray: Fields = [
			...(!jobId ? [formFields.job(jobs)] : []),
			[
				formFields.datetime({
					required: true,
				}),
				formFields.interviewType(),
			],
			[
				formFields.interviewAttendanceType(),
				formFields.location(locations, locationModalRef, null, null, {
					displayCondition: (formData: JobData): boolean => {
						return formData.attendance_type === "on-site";
					},
				}),
			],
			formFields.interviewers(persons, personModalRef),
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
					ref={ref}
					size={size}
					fields={fields}
					endpoint="interviews"
					itemName="Interview"
					transformFormData={transformFormData}
				/>

				<LocationModal ref={locationModalRef} />
				<PersonModal ref={personModalRef} />
			</>
		);
	},
);
