import React, { useCallback, useEffect, useRef, useState } from "react";
import GenericModal from "../GenericModal";
import useGenericAlert from "../../../hooks/useGenericAlert";
import { api } from "../../../services/api";
import { useAuth } from "../../../contexts/AuthContext";
import AlertModal from "../alert/AlertModal";

const InterviewFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false, jobApplicationId }) => {
	const { token } = useAuth();
	const { alertState, showError, hideAlert } = useGenericAlert();
	const formRef = useRef();

	// State for dropdown options and interview data
	const [locations, setLocations] = useState([]);
	const [jobApplications, setJobApplications] = useState([]);
	const [interviewData, setInterviewData] = useState({});
	const [loading, setLoading] = useState(false);
	const [dataLoaded, setDataLoaded] = useState(false);

	// Load data when modal opens
	useEffect(() => {
		if (show) {
			setDataLoaded(false);
			loadData();
		} else {
			// Reset state when modal closes
			setInterviewData({});
			setDataLoaded(false);
		}
	}, [show, token, initialData?.id, isEdit]);

	const loadData = async () => {
		setLoading(true);
		try {
			// Load dropdown data first
			await loadDropdownData();

			// Load interview data if editing
			if (isEdit && initialData?.id) {
				await loadInterviewData(initialData.id);
			} else {
				// For new interviews, set default data
				setInterviewData({
					date: "",
					location_id: "",
					note: "",
					...(jobApplicationId && !isEdit ? { jobapplication_id: jobApplicationId } : {}),
				});
			}

			setDataLoaded(true);
		} catch (error) {
			console.error("Error loading data:", error);
			showError({
				title: "Data Loading Error",
				message: "Error loading form data. Please try again.",
				size: "md",
			});
		} finally {
			setLoading(false);
		}
	};

	const loadDropdownData = async () => {
		try {
			// Load locations
			const locationsData = await api.get("locations", token);
			setLocations(
				locationsData.map((location) => ({
					value: location.id,
					label: `${location.name} - ${location.city}, ${location.country}`,
				})),
			);

			// Load job applications if not passed as prop
			if (!jobApplicationId) {
				const jobApplicationsData = await api.get("jobapplications", token);
				setJobApplications(
					jobApplicationsData.map((jobApp) => ({
						value: jobApp.id,
						label: `${jobApp.job?.title} at ${jobApp.job?.company?.name} (${jobApp.status})`,
					})),
				);
			}
		} catch (error) {
			console.error("Error loading dropdown data:", error);
			throw error; // Re-throw to be caught by parent loadData function
		}
	};

	const loadInterviewData = async (interviewId) => {
		try {
			console.log("Fetching interview data for ID:", interviewId);
			const interview = await api.get(`interviews/${interviewId}`, token);
			console.log("Fetched interview data:", interview);
			setInterviewData(interview);
		} catch (error) {
			console.error("Error loading interview data:", error);
			showError({
				title: "Interview Loading Error",
				message: "Error loading interview data. Please try again.",
				size: "md",
			});
			throw error;
		}
	};

	// Transform data to match form field expectations
	const transformDataForForm = useCallback(
		(data) => {
			console.log("Transform data for form input:", data);

			if (!data || Object.keys(data).length === 0) {
				const defaultData = {
					date: "",
					location_id: "",
					note: "",
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

			console.log("Transformed data output:", transformed);
			return transformed;
		},
		[jobApplicationId, isEdit],
	);

	// Define layout groups for interview fields
	const layoutGroups = [
		{
			id: "interview-date-location",
			type: "row",
			fields: [
				{
					name: "date",
					label: "Interview Date & Time",
					type: "datetime-local",
					required: true,
					columnClass: "col-md-8",
					placeholder: "Select interview date and time",
				},
				{
					name: "location_id",
					label: "Location",
					type: "select",
					options: locations,
					columnClass: "col-md-4",
					placeholder: "Select location (optional)",
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
							options: jobApplications,
							required: true,
							placeholder: "Select job application",
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
	];

	// Data transformation function for form submission
	const transformFormData = (data) => {
		console.log("Transforming interview form data for submission:", data);

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

		// Remove system fields that shouldn't be sent to backend
		delete transformed.created_at;
		delete transformed.modified_at;
		delete transformed.owner_id;
		delete transformed.location;
		delete transformed.job_application;
		delete transformed.interviewers;

		// Clean up empty values but preserve legitimate empty strings for notes
		const cleanedData = Object.fromEntries(
			Object.entries(transformed).filter(([key, value]) => {
				if (value === null || value === undefined) return key === "location_id"; // Allow null for optional location
				if (typeof value === "string" && value === "" && key !== "note") return false;
				return true;
			}),
		);

		console.log("Final transformed interview data:", cleanedData);
		return cleanedData;
	};

	// Don't render the modal until data is loaded
	if (show && !dataLoaded) {
		return (
			<>
				<GenericModal
					show={show}
					onHide={onHide}
					mode="form"
					title="Interview"
					size={size}
					loading={loading}
					loadingMessage="Loading interview data..."
				/>
				<AlertModal alertState={alertState} hideAlert={hideAlert} />
			</>
		);
	}

	// Prepare data for the form
	const preparedData = transformDataForForm(interviewData);

	return (
		<>
			<GenericModal
				ref={formRef}
				show={show}
				onHide={onHide}
				mode="form"
				title={isEdit ? "Edit Interview" : "Add Interview"}
				size={size}
				useCustomLayout={true}
				layoutGroups={layoutGroups}
				initialData={preparedData}
				transformFormData={transformFormData}
				endpoint="interviews"
				onSuccess={onSuccess}
				isEdit={isEdit}
				loading={loading}
			/>

			{/* Alert Modal for error messages */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};

export default InterviewFormModal;
