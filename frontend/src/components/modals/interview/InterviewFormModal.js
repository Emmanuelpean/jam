import React, { useEffect, useState, useMemo } from "react";
import { useAuth } from "../../../contexts/AuthContext";
import GenericModal from "../GenericModal";
import LocationFormModal from "../location/LocationFormModal";
import PersonFormModal from "../person/PersonFormModal";
import AlertModal from "../alert/AlertModal";
import useGenericAlert from "../../../hooks/useGenericAlert";
import {
	apiHelpers,
	jobApplicationsApi,
	locationsApi,
	personsApi,
} from "../../../services/api";

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

	// Interview type options
	const interviewTypeOptions = [
		{ value: "HR", label: "HR Interview" },
		{ value: "Technical", label: "Technical Interview" },
		{ value: "Management", label: "Management Interview" },
		{ value: "Panel", label: "Panel Interview" },
		{ value: "Phone", label: "Phone Interview" },
		{ value: "Video", label: "Video Interview" },
		{ value: "Assessment", label: "Assessment/Test" },
		{ value: "Final", label: "Final Interview" },
		{ value: "Other", label: "Other" },
	];

	// Fetch all options for the select fields
	useEffect(() => {
		const fetchOptions = async () => {
			if (!token || !show) return;

			setLoading(true);
			try {
				// Use your existing API structure
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
					}))
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
		console.log("Transform initial data for form:", data);

		if (!data || Object.keys(data).length === 0) {
			const defaultData = {
				date: "",
				type: "",
				location_id: "",
				note: "",
				interviewers: [],
			};

			// Set jobapplication_id from prop if provided for new interviews
			if (jobApplicationId && !isEdit) {
				defaultData.jobapplication_id = jobApplicationId;
			}

			console.log("Using default data:", defaultData);
			return defaultData;
		}

		const transformed = { ...data };

		// Convert ISO datetime to datetime-local format for the input
		if (transformed.date) {
			const date = new Date(transformed.date);
			// Validate the date
			if (!isNaN(date.getTime())) {
				// Convert to local datetime string format (YYYY-MM-DDTHH:MM)
				const year = date.getFullYear();
				const month = String(date.getMonth() + 1).padStart(2, "0");
				const day = String(date.getDate()).padStart(2, "0");
				const hours = String(date.getHours()).padStart(2, "0");
				const minutes = String(date.getMinutes()).padStart(2, "0");
				transformed.date = `${year}-${month}-${day}T${hours}:${minutes}`;
			} else {
				transformed.date = "";
			}
		} else {
			transformed.date = "";
		}

		// Ensure required fields are not null/undefined
		if (transformed.type === null || transformed.type === undefined) {
			transformed.type = "";
		}

		// Ensure note field is not null/undefined
		if (transformed.note === null || transformed.note === undefined) {
			transformed.note = "";
		}

		// Handle location_id - ensure it's properly set for the select
		if (transformed.location_id === null || transformed.location_id === undefined) {
			transformed.location_id = "";
		}

		// Handle jobapplication_id - ensure it's properly set for the select
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

		console.log("Transformed initial data output:", transformed);
		return transformed;
	};

	// Define layout groups for interview fields using useMemo to update when options change
	const layoutGroups = useMemo(() => [
		{
			id: "interview-basic-info",
			type: "row",
			fields: [
				{
					name: "date",
					label: "Interview Date & Time",
					type: "datetime-local",
					required: true,
					columnClass: "col-md-6",
					placeholder: "Select interview date and time",
				},
				{
					name: "type",
					label: "Interview Type",
					type: "select",
					required: true,
					options: interviewTypeOptions,
					placeholder: "Select interview type",
					columnClass: "col-md-6",
				},
			],
		},
		{
			id: "interview-location",
			type: "default",
			fields: [
				{
					name: "location_id",
					label: "Location",
					type: "select",
					placeholder: "Select or search location...",
					isSearchable: true,
					isClearable: true,
					options: locationOptions,
					addButton: {
						onClick: () => setShowLocationModal(true),
					},
				},
			],
		},
		{
			id: "interview-job-application",
			type: "default",
			fields: jobApplicationId
				? []
				: [
					{
						name: "jobapplication_id",
						label: "Job Application",
						type: "select",
						options: jobApplicationOptions,
						required: true,
						placeholder: "Select job application",
						isSearchable: true,
					},
				],
		},
		{
			id: "interview-contacts",
			type: "default",
			fields: [
				{
					name: "interviewers",
					label: "Interviewers/Contacts",
					type: "multiselect",
					placeholder: "Select interviewers and contacts...",
					isSearchable: true,
					options: personOptions,
					addButton: {
						onClick: () => setShowPersonModal(true),
					},
				},
			],
		},
		{
			id: "interview-notes",
			type: "default",
			fields: [
				{
					name: "note",
					label: "Interview Notes",
					type: "textarea",
					placeholder: "Add notes about the interview, questions asked, impressions, etc...",
				},
			],
		},
	], [locationOptions, jobApplicationOptions, personOptions, jobApplicationId]);


// In your transformFormData function, add this logging at the very end:
	const transformFormData = (data) => {
		console.log("=== INTERVIEW FORM DATA TRANSFORMATION DEBUG ===");
		console.log("Raw form data received:", JSON.stringify(data, null, 2));

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
		console.log("Interviewers raw:", transformed.interviewers, "Type:", typeof transformed.interviewers);
		if (transformed.interviewers && Array.isArray(transformed.interviewers)) {
			transformed.interviewers = transformed.interviewers
				.map((id) => {
					const converted = typeof id === "string" ? parseInt(id, 10) : id;
					console.log(`Converting interviewer: ${id} (${typeof id}) -> ${converted} (${typeof converted})`);
					return converted;
				})
				.filter((id) => !isNaN(id));
			console.log("Final interviewers array:", transformed.interviewers);
		} else {
			console.log("Interviewers is not an array, setting to empty array");
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
			})
		);

		console.log("=== FINAL DATA TO BE SENT TO API ===");
		console.log(JSON.stringify(cleanedData, null, 2));
		console.log("Interviewers specifically:", cleanedData.interviewers);
		console.log("=== END TRANSFORMATION DEBUG ===");

		return cleanedData;
	};

	// Prepare the initial data using the transform function
	const preparedInitialData = transformInitialData(initialData);

	return (
		<>
			<GenericModal
				show={show}
				onHide={onHide}
				mode="form"
				title={isEdit ? "Edit Interview" : "Add Interview"}
				size={size}
				useCustomLayout={true}
				layoutGroups={layoutGroups}
				initialData={preparedInitialData}
				transformFormData={transformFormData}
				endpoint="interviews"
				onSuccess={onSuccess}
				isEdit={isEdit}
				loading={loading}
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