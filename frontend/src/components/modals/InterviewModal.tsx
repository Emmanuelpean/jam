import React, { useMemo, useState, useEffect } from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields, useFormOptions } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { formatDateTime } from "../../utils/TimeUtils";
import { DataModalProps } from "./AggregatorModal";
import { InterviewData } from "../../services/Schemas";

interface InterviewModalProps extends DataModalProps {
	jobApplicationId?: string | number;
}

export const InterviewModal: React.FC<InterviewModalProps> = ({
	show,
	onHide,
	data,
	id,
	onSuccess,
	onDelete,
	submode = "view",
	size = "sm",
	jobApplicationId,
}) => {
	const { locations, persons, jobs, openLocationModal, openPersonModal, renderLocationModal, renderPersonModal } =
		useFormOptions(["locations", "persons", "jobs"]);

	const [currentFormData, setCurrentFormData] = useState<InterviewData>({});

	const initialData = useMemo(() => {
		if (submode === "add" && !data?.id) {
			return { date: formatDateTime() };
		}
		return data || {};
	}, [data, submode]);

	// Initialize current form data when modal opens or data changes
	useEffect(() => {
		if (show) {
			setCurrentFormData(initialData);
		}
	}, [show, initialData]);

	// Handler for form data changes
	const handleFormDataChange = (newFormData: InterviewData) => {
		setCurrentFormData((prev) => ({
			...prev,
			...newFormData,
		}));
	};

	const formFieldsArray = [
		...(!jobApplicationId ? [formFields.job(jobs)] : []),
		[
			formFields.datetime({
				required: true,
			}),
			formFields.interviewType(),
		],
		[
			formFields.interviewAttendanceType(),
			...(currentFormData?.attendance_type !== "remote"
				? [formFields.location(locations, openLocationModal)]
				: []),
		],
		formFields.interviewers(persons, openPersonModal),
		formFields.note({
			placeholder: "Add notes about the interview, questions asked, impressions, etc...",
		}),
	];

	const viewFieldsArray = [
		...(!jobApplicationId ? [viewFields.job({ label: "Job Application" })] : []),
		[viewFields.datetime(), viewFields.type()],
		[viewFields.location(), viewFields.interviewers()],
		viewFields.note(),
	];

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const transformFormData = (data: InterviewData) => {
		console.log(data);
		return {
			date: new Date(data.date!).toISOString(),
			type: data.type!,
			location_id: data.location_id!,
			job_application_id: jobApplicationId || data.job_application_id!,
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
				data={initialData}
				id={id}
				fields={fields}
				endpoint="interviews"
				onSuccess={onSuccess}
				onDelete={onDelete}
				transformFormData={transformFormData}
				onFormDataChange={handleFormDataChange}
			/>

			{renderLocationModal()}

			{renderPersonModal()}
		</>
	);
};
