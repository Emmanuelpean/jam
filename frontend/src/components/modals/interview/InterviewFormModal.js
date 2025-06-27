import React, { useEffect, useState } from "react";
import { useAuth } from "../../../contexts/AuthContext";
import GenericModal from "../GenericModal";
import LocationFormModal from "../location/LocationFormModal";
import PersonFormModal from "../person/PersonModal";
import AlertModal from "../alert/AlertModal";
import useGenericAlert from "../../../hooks/useGenericAlert";
import { formFields } from "../../rendering/FormRenders";
import { apiHelpers, jobApplicationsApi, locationsApi, personsApi } from "../../../services/api";
import { formDateTime } from "../../../utils/TimeUtils";

const InterviewFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false, jobApplicationId }) => {
	const { token } = useAuth();
	const { alertState, showError, hideAlert } = useGenericAlert();

	// State for dropdown options and modals
	const [locationOptions, setLocationOptions] = useState([]);
	const [jobApplicationOptions, setJobApplicationOptions] = useState([]);
	const [personOptions, setPersonOptions] = useState([]);
	const [loading, setLoading] = useState(false);
	const [showLocationModal, setShowLocationModal] = useState(false);
	const [showPersonModal, setShowPersonModal] = useState(false);

	// Fetch all options for the select fields
	useEffect(() => {
		const fetchOptions = async () => {
			if (!token || !show) return;

			setLoading(true);
			try {
				const [locationsData, jobApplicationsData, personsData] = await Promise.all([
					locationsApi.getAll(token),
					jobApplicationsApi.getAll(token),
					personsApi.getAll(token),
				]);

				setLocationOptions(apiHelpers.toSelectOptions(locationsData));
				setJobApplicationOptions(
					jobApplicationsData.map((jobApp) => ({
						value: jobApp.id,
						label: `${jobApp.job.name}`,
					})),
				);
				setPersonOptions(apiHelpers.toSelectOptions(personsData));
			} catch (error) {
				console.error("Error fetching options:", error);
				showError({
					title: "Data Loading Error",
					message: "Error loading form data. Please try again.",
					size: "md",
				});
			} finally {
				setLoading(false);
			}
		};

		fetchOptions();
	}, [token, show]);

	// Handle successful location creation
	const handleLocationSuccess = (newLocation) => {
		const newOption = {
			value: newLocation.id,
			label: newLocation.name,
		};
		setLocationOptions((prev) => [...prev, newOption]);
		setShowLocationModal(false);
	};

	// Handle successful person creation
	const handlePersonSuccess = (newPerson) => {
		const newOption = {
			value: newPerson.id,
			label: newPerson.name,
		};
		setPersonOptions((prev) => [...prev, newOption]);
		setShowPersonModal(false);
	};

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
			if (jobApplicationId && !isEdit) {
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
			if (jobApplicationId && !isEdit) {
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

	// Define interview fields using the new simplified structure
	const interviewFields = [
		[
			formFields.datetime({
				label: "Interview Date & Time",
				required: true,
			}),
			formFields.interviewType(),
		],

		formFields.location(locationOptions, () => setShowLocationModal(true)),
		formFields.jobApplication(jobApplicationOptions),
		formFields.interviewers(personOptions, () => setShowPersonModal(true)),
		formFields.note({
			placeholder: "Add notes about the interview, questions asked, impressions, etc...",
		}),
	];

	const transformFormData = (data) => {
		const transformed = { ...data };

		// Convert datetime-local back to ISO format
		if (transformed.date) {
			transformed.date = new Date(transformed.date).toISOString();
		}

		// Add jobapplication_id for new interviews if passed as prop
		if (!isEdit && jobApplicationId) {
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
				mode="form"
				title="Interview"
				size={size}
				fields={interviewFields}
				initialData={transformInitialData(initialData)}
				transformFormData={transformFormData}
				endpoint="interviews"
				onSuccess={onSuccess}
				isEdit={isEdit}
			/>

			{/* Location Form Modal */}
			<LocationFormModal
				show={showLocationModal}
				onHide={() => setShowLocationModal(false)}
				onSuccess={handleLocationSuccess}
			/>

			{/* Person Form Modal */}
			<PersonFormModal
				show={showPersonModal}
				onHide={() => setShowPersonModal(false)}
				onSuccess={handlePersonSuccess}
			/>

			{/* Alert Modal for error messages */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};

export default InterviewFormModal;
