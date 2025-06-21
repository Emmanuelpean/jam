import React, { useCallback, useEffect, useRef, useState } from "react";
import GenericModal from "../GenericModal";
import useGenericAlert from "../../../hooks/useGenericAlert";
import { api, filesApi } from "../../../services/api";
import { useAuth } from "../../../contexts/AuthContext";
import AlertModal from "../alert/AlertModal";
import { fileToBase64 } from "../../../utils/FileUtils";
import InterviewsTable from "../../tables/InterviewTable";
import { formFields } from "../../rendering/FormRenders";

const JobApplicationFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false, jobId }) => {
	const { token } = useAuth();
	const { alertState, showError, hideAlert } = useGenericAlert();
	const formRef = useRef();

	// Track file states independently
	const [fileStates, setFileStates] = useState({
		cv: null,
		cover_letter: null,
	});

	// Track interview data
	const [interviews, setInterviews] = useState([]);
	const [refreshInterviews, setRefreshInterviews] = useState(0);

	// Initialize file states when modal opens or initialData changes
	useEffect(() => {
		if (show) {
			setFileStates({
				cv: initialData?.cv || null,
				cover_letter: initialData?.cover_letter || null,
			});
			setInterviews(initialData?.interviews || []);
		}
	}, [show, initialData?.cv, initialData?.cover_letter, initialData?.interviews]);

	// Refresh interviews when needed
	useEffect(() => {
		if (show && isEdit && initialData?.id && refreshInterviews > 0) {
			refreshJobApplicationData();
		}
	}, [refreshInterviews, show, isEdit, initialData?.id, token]);

	const refreshJobApplicationData = async () => {
		try {
			const updatedJobApplication = await api.get(`jobapplications/${initialData.id}`, token);
			setInterviews(updatedJobApplication.interviews || []);
		} catch (error) {
			console.error("Error refreshing job application data:", error);
		}
	};

	const handleInterviewChange = () => {
		setRefreshInterviews((prev) => prev + 1);
	};

	const handleFileDownload = async (fileObject) => {
		try {
			await filesApi.download(fileObject.id, fileObject.filename, token);
		} catch (error) {
			console.error("Error downloading file:", error);
			showError({
				title: "Download Error",
				message: "Error downloading file. Please try again.",
				size: "md",
			});
		}
	};

	// Custom file change handler that tracks file state
	const handleFileChange = useCallback((fieldName, file) => {
		console.log(`File changed for ${fieldName}:`, file);
		setFileStates((prev) => ({
			...prev,
			[fieldName]: file,
		}));
	}, []);

	// Custom file remove handler
	const handleFileRemove = useCallback((fieldName) => {
		console.log(`File removed for ${fieldName}`);
		setFileStates((prev) => ({
			...prev,
			[fieldName]: null,
		}));
	}, []);

	// Helper function to normalize content for comparison
	const normalizeFileContent = (content) => {
		if (!content) return "";

		// If it's a data URL, extract just the base64 part
		if (content.startsWith("data:")) {
			const base64Index = content.indexOf(",");
			if (base64Index !== -1) {
				return content.substring(base64Index + 1);
			}
		}

		// If it's already base64 encoded data URL, decode it first
		try {
			const decoded = atob(content);
			if (decoded.startsWith("data:")) {
				const base64Index = decoded.indexOf(",");
				if (base64Index !== -1) {
					return decoded.substring(base64Index + 1);
				}
			}
		} catch (e) {
			// If decoding fails, it's probably already just base64
		}

		return content;
	};

	// Process a single file: check for existing or create new
	const processFile = async (file) => {
		if (!file || !(file instanceof File)) {
			return null;
		}

		try {
			// Convert file to base64
			const base64Content = await fileToBase64(file);
			const normalizedNewContent = normalizeFileContent(base64Content);

			// Check for existing files
			const files = await filesApi.getAll(token);

			const existingFile = files.find((f) => {
				const normalizedExistingContent = normalizeFileContent(f.content);
				return f.filename === file.name && normalizedExistingContent === normalizedNewContent;
			});

			if (existingFile) {
				console.log(`File ${file.name} already exists, reusing ID: ${existingFile.id}`);
				return existingFile.id;
			} else {
				// Create new file entry
				console.log(`Creating new file entry for: ${file.name}`);
				const fileData = {
					filename: file.name,
					content: base64Content, // Store the full data URL
					type: file.type,
					size: file.size,
				};

				const newFile = await filesApi.create(fileData, token);
				console.log(`File created with ID: ${newFile.id}`);
				return newFile.id;
			}
		} catch (error) {
			console.error(`Error processing file ${file.name}:`, error);

			// Check if error has validation details
			if (error.data && error.data.detail) {
				// If it's a validation error, extract a meaningful message
				if (Array.isArray(error.data.detail)) {
					const messages = error.data.detail.map((err) => err.msg || JSON.stringify(err)).join(", ");
					throw new Error(`File validation error: ${messages}`);
				} else if (typeof error.data.detail === "string") {
					throw new Error(error.data.detail);
				} else {
					throw new Error(`File processing failed: ${JSON.stringify(error.data.detail)}`);
				}
			}

			throw error;
		}
	};

	// Transform initial data to match form field expectations
	const transformInitialData = useCallback((data) => {
		if (!data || Object.keys(data).length === 0) return data;

		const transformed = { ...data };

		// Convert ISO datetime to datetime-local format for the input
		if (transformed.date) {
			const date = new Date(transformed.date);
			// Convert to local datetime string format (YYYY-MM-DDTHH:MM)
			const year = date.getFullYear();
			const month = String(date.getMonth() + 1).padStart(2, "0");
			const day = String(date.getDate()).padStart(2, "0");
			const hours = String(date.getHours()).padStart(2, "0");
			const minutes = String(date.getMinutes()).padStart(2, "0");
			transformed.date = `${year}-${month}-${day}T${hours}:${minutes}`;
		}

		// Ensure string fields are not null/undefined
		if (transformed.url === null || transformed.url === undefined) {
			transformed.url = "";
		}
		if (transformed.note === null || transformed.note === undefined) {
			transformed.note = "";
		}

		return transformed;
	}, []);

	// Define job application fields using the new simplified structure
	const jobApplicationFields = [
		[formFields.applicationDate(), formFields.applicationStatus()],
		formFields.applicationUrl(),
		formFields.note({
			label: "Application Notes",
			placeholder: "Add notes about your application process, interview details, etc...",
		}),
		[
			{
				name: "cv",
				label: "CV/Resume",
				type: "drag-drop",
				value: fileStates.cv,
				onChange: (file) => handleFileChange("cv", file),
				onRemove: () => handleFileRemove("cv"),
				onOpenFile: handleFileDownload,
			},
			{
				name: "cover_letter",
				label: "Cover Letter",
				type: "drag-drop",
				value: fileStates.cover_letter,
				onChange: (file) => handleFileChange("cover_letter", file),
				onRemove: () => handleFileRemove("cover_letter"),
				onOpenFile: handleFileDownload,
			},
		],
	];


	// Custom submit handler to process files before form submission
	const handleCustomSubmit = async (formElement, submitCallback) => {

		try {
			// Get form data from the actual form element
			const formData = new FormData(formElement);
			const transformedData = {};

			// Process regular form fields first
			for (const [key, value] of formData.entries()) {
				if (typeof value === "string") {
					transformedData[key] = value;
				}
			}

			// Process file states instead of relying on form files
			const fileFields = ["cv", "cover_letter"];

			for (const fieldName of fileFields) {
				const currentFile = fileStates[fieldName];
				const idFieldName = `${fieldName}_id`;

				if (currentFile === null) {
					// File was explicitly removed - send null to backend
					transformedData[idFieldName] = null;
				} else if (currentFile instanceof File) {
					// New file uploaded
					try {
						const fileId = await processFile(currentFile);
						transformedData[idFieldName] = fileId;
					} catch (fileError) {
						console.error(`Error processing file ${fieldName}:`, fileError);
						throw new Error(`Failed to process ${fieldName}: ${fileError.message}`);
					}
				} else if (currentFile && typeof currentFile === "object" && currentFile.id) {
					// Existing file from database - keep the ID
					transformedData[idFieldName] = currentFile.id;
				} else {
					// No file state for this field - explicitly set to null for updates
					if (isEdit) {
						transformedData[idFieldName] = null;
					}
					// For new records, don't set the field at all
				}
			}

			// Now submit the form with file IDs
			await submitCallback(transformedData);
		} catch (error) {
			console.error("Error processing files:", error);

			// Extract meaningful error message
			let errorMessage = "Failed to process uploaded files. Please try again.";
			if (error.message) {
				errorMessage = error.message;
			}

			showError({
				title: "File Processing Error",
				message: errorMessage,
				size: "md",
			});
			throw error; // Re-throw to prevent form submission
		}
	};

	// Data transformation function (synchronous - files already processed)
	const transformFormData = (data) => {

		const transformed = { ...data };

		// Convert datetime-local back to ISO format
		if (transformed.date) {
			transformed.date = new Date(transformed.date).toISOString();
		}

		// Add job_id for new applications
		if (!isEdit && jobId) {
			transformed.job_id = jobId;
		}

		// Remove system fields that shouldn't be sent to backend
		delete transformed.created_at;
		delete transformed.modified_at;
		delete transformed.owner_id;
		delete transformed.job;
		delete transformed.interviews;

		// Clean up empty values but preserve null file IDs
		const cleanedData = Object.fromEntries(
			Object.entries(transformed).filter(([key, value]) => {
				// Always include file ID fields, even if null (indicates removal)
				if (key.endsWith("_id")) return true;
				if (value === null || value === undefined) return false;
				// Allow empty strings for url and note fields
				if (typeof value === "string" && value === "" && key !== "url" && key !== "note") return false;
				return true;
			}),
		);

		return cleanedData;
	};

	// Custom content to include the interviews table for edit mode
	const customContent =
		isEdit && initialData?.id ? (
			<InterviewsTable
				interviews={interviews}
				jobApplicationId={initialData.id}
				onInterviewChange={handleInterviewChange}
			/>
		) : null;

	return (
		<>
			<GenericModal
				ref={formRef}
				show={show}
				onHide={onHide}
				mode="form"
				title="Job Application"
				size={size}
				fields={jobApplicationFields}
				initialData={transformInitialData(initialData)}
				transformFormData={transformFormData}
				endpoint="jobapplications"
				onSuccess={onSuccess}
				isEdit={isEdit}
				customSubmitHandler={handleCustomSubmit}
				customContent={customContent}
			/>

			{/* Alert Modal for error messages */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};

export default JobApplicationFormModal;
