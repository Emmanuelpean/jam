import React, { useEffect, useState } from "react";
import { useAuth } from "../../../contexts/AuthContext";
import GenericModal from "../GenericModal";
import AlertModal from "../alert/AlertModal";
import useGenericAlert from "../../../hooks/useGenericAlert";
import { formFields, useFormOptions } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";
import { jobApplicationsApi } from "../../../services/api";
import { formDateTime } from "../../../utils/TimeUtils";

export const InterviewModal = ({
	show,
	onHide,
	interview,
	onSuccess,
	onDelete,
	endpoint = "interviews",
	submode = "view",
	size = "lg",
	jobApplicationId,
}) => {
	const { token } = useAuth();
	const { alertState, showError, hideAlert } = useGenericAlert();

	// Use the existing useFormOptions hook
	const { locations, persons, openLocationModal, openPersonModal, renderLocationModal, renderPersonModal } =
		useFormOptions();

	// State for job applications only (since it's specific to interviews)
	const [jobApplicationOptions, setJobApplicationOptions] = useState([]);
	const [loading, setLoading] = useState(false);

	// Fetch job application options
	useEffect(() => {
		const fetchJobApplications = async () => {
			if (!token || !show || submode === "view") return;

			setLoading(true);
			try {
				const jobApplicationsData = await jobApplicationsApi.getAll(token);
				setJobApplicationOptions(
					jobApplicationsData.map((jobApp) => ({
						value: jobApp.id,
						label: `${jobApp.job.name}`,
					})),
				);
			} catch (error) {
				console.error("Error fetching job applications:", error);
				showError({
					title: "Data Loading Error",
					message: "Error loading job applications. Please try again.",
					size: "md",
				});
			} finally {
				setLoading(false);
			}
		};

		fetchJobApplications();
	}, [token, show, submode]);

	// Don't render if we're in view mode but have no interview data
	if (submode === "view" && !interview?.id) {
		return null;
	}

	// Transform initial data to match form field expectations
	const transformInitialData = (data) => {
		if (!data || Object.keys(data).length === 0) {
			const defaultData = {
				date: formDateTime(),
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

		transformed.date = formDateTime(transformed.date);

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

	// Form fields for editing
	const formFieldsArray = [
		[
			formFields.datetime({
				label: "Interview Date & Time",
				required: true,
			}),
			formFields.interviewType(),
		],
		formFields.location(locations, openLocationModal),
		formFields.jobApplication(jobApplicationOptions),
		formFields.interviewers(persons, openPersonModal),
		formFields.note({
			placeholder: "Add notes about the interview, questions asked, impressions, etc...",
		}),
	];

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
				data={interview || {}}
				fields={fields}
				endpoint={endpoint}
				onSuccess={onSuccess}
				onDelete={onDelete}
				initialData={transformInitialData(interview)}
				transformFormData={transformFormData}
			/>

			{renderLocationModal()}

			{renderPersonModal()}

			{/* Alert Modal for error messages */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};

export const InterviewFormModal = (props) => {
	// Determine the submode based on whether we have interview data with an ID
	const submode = props.isEdit || props.interview?.id ? "edit" : "add";
	return <InterviewModal {...props} submode={submode} />;
};

// Wrapper for view modal
export const InterviewViewModal = (props) => <InterviewModal {...props} interview={props.item} submode="view" />;

// Add default export
export default InterviewFormModal;
