import React from "react";
import GenericModal from "../GenericModal";
import { formFields, useFormOptions } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";
import { formatDateTime } from "../../../utils/TimeUtils";

export const InterviewModal = ({
	show,
	onHide,
	data,
	onSuccess,
	onDelete,
	endpoint = "interviews",
	submode = "view",
	size = "lg",
	jobApplicationId,
}) => {
	const {
		locations,
		persons,
		jobApplications,
		openLocationModal,
		openPersonModal,
		openJobApplicationModal,
		renderLocationModal,
		renderPersonModal,
		renderJobApplicationModal,
	} = useFormOptions();

	const transformInitialData = (data) => {
		if (!data || Object.keys(data).length === 0) {
			const defaultData = {
				date: formatDateTime(),
				type: "",
				location_id: "",
				note: "",
				interviewers: [],
			};

			// Set jobapplication_id from prop if provided for new interviews
			if (jobApplicationId && (submode === "add" || !data?.id)) {
				defaultData.jobapplication_id = jobApplicationId;
			}

			return defaultData;
		}

		const transformed = { ...data };

		transformed.date = formatDateTime(transformed.date);

		// Ensure required fields are not null/undefined
		if (transformed.type === null || transformed.type === undefined) {
			transformed.type = "";
		}

		if (transformed.note === null || transformed.note === undefined) {
			transformed.note = "";
		}

		if (transformed.location_id === null || transformed.location_id === undefined) {
			transformed.location_id = "";
		}

		if (transformed.jobapplication_id === null || transformed.jobapplication_id === undefined) {
			if (jobApplicationId && submode === "add") {
				transformed.jobapplication_id = jobApplicationId;
			} else {
				transformed.jobapplication_id = "";
			}
		}

		// Handle interviewers - convert from objects to IDs for multiselect
		if (transformed.interviewers && Array.isArray(transformed.interviewers)) {
			transformed.interviewers = transformed.interviewers.map((interviewer) => {
				return typeof interviewer === "object" ? interviewer.id : interviewer;
			});
		} else {
			transformed.interviewers = [];
		}

		return transformed;
	};

	const formFieldsArray = [
		[
			formFields.datetime({
				label: "Interview Date & Time",
				required: true,
			}),
			formFields.interviewType(),
		],
		formFields.location(locations, openLocationModal),
		formFields.jobApplication(jobApplications, openJobApplicationModal),
		formFields.interviewers(persons, openPersonModal),
		formFields.note({
			placeholder: "Add notes about the interview, questions asked, impressions, etc...",
		}),
	];
	console.log("jobs app", jobApplications);
	console.log("persons", persons);
	console.log("locations", locations);

	// View fields for display
	const viewFieldsArray = [
		[viewFields.date(), viewFields.type()],
		[viewFields.location(), viewFields.interviewers()],
		viewFields.note(),
	];

	// Combine them in a way GenericModal can use based on mode
	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	// Transform form data before submission
	const transformFormData = (data) => {
		const transformed = { ...data };

		// Convert datetime-local back to ISO format
		if (transformed.date) {
			transformed.date = new Date(transformed.date).toISOString();
		}

		// Add jobapplication_id for new interviews if passed as prop
		if (submode === "add" && jobApplicationId) {
			transformed.jobapplication_id = jobApplicationId;
		}

		// Convert empty strings to null for optional foreign keys
		if (transformed.location_id === "") {
			transformed.location_id = null;
		}

		// Convert location_id to number if it's a string
		if (transformed.location_id && typeof transformed.location_id === "string") {
			transformed.location_id = parseInt(transformed.location_id, 10);
		}

		// Convert jobapplication_id to number if it's a string
		if (transformed.jobapplication_id && typeof transformed.jobapplication_id === "string") {
			transformed.jobapplication_id = parseInt(transformed.jobapplication_id, 10);
		}

		// Handle interviewers array - ensure it contains only numbers
		if (transformed.interviewers && Array.isArray(transformed.interviewers)) {
			transformed.interviewers = transformed.interviewers
				.map((id) => {
					const converted = typeof id === "string" ? parseInt(id, 10) : id;
					return converted;
				})
				.filter((id) => !isNaN(id));
		} else {
			transformed.interviewers = [];
		}

		// Remove system fields that shouldn't be sent to backend
		delete transformed.created_at;
		delete transformed.modified_at;
		delete transformed.owner_id;
		delete transformed.location;
		delete transformed.job_application;

		// Clean up empty values but preserve legitimate empty strings for notes and empty arrays for interviewers
		const cleanedData = Object.fromEntries(
			Object.entries(transformed).filter(([key, value]) => {
				if (value === null || value === undefined) return key === "location_id"; // Allow null for optional location
				if (typeof value === "string" && value === "" && key !== "note") return false;
				if (Array.isArray(value) && key === "interviewers") return true; // Keep empty interviewers array
				return true;
			}),
		);

		return cleanedData;
	};

	return (
		<>
			<GenericModal
				show={show}
				onHide={onHide}
				mode="formview"
				submode={submode}
				title="Interview"
				size={size}
				data={data || {}}
				fields={fields}
				endpoint={endpoint}
				onSuccess={onSuccess}
				onDelete={onDelete}
				// initialData={transformInitialData(data)}
				transformFormData={transformFormData}
			/>

			{renderLocationModal()}

			{renderPersonModal()}

			{renderJobApplicationModal()}
		</>
	);
};

export const InterviewFormModal = (props) => {
	const submode = props.isEdit || props.interview?.id ? "edit" : "add";
	return <InterviewModal {...props} submode={submode} />;
};

// Wrapper for view modal
export const InterviewViewModal = (props) => <InterviewModal {...props} interview={props.item} submode="view" />;

// Add default export
export default InterviewFormModal;
