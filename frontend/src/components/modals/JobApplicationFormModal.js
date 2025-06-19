import React, { useRef } from "react";
import GenericModal from "../GenericModal";
import useGenericAlert from "../../hooks/useGenericAlert";
import { filesApi } from "../../services/api";
import { useAuth } from "../../contexts/AuthContext";
import AlertModal from "../AlertModal";
import { fileToBase64 } from "../../utils/FileUtils";

const JobApplicationFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false, jobId }) => {
	const { token } = useAuth();
	const { alertState, showError, hideAlert } = useGenericAlert();
	const formRef = useRef();

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

	// Helper function to normalize content for comparison
	const normalizeFileContent = (content) => {
		if (!content) return '';

		// If it's a data URL, extract just the base64 part
		if (content.startsWith('data:')) {
			const base64Index = content.indexOf(',');
			if (base64Index !== -1) {
				return content.substring(base64Index + 1);
			}
		}

		// If it's already base64 encoded data URL, decode it first
		try {
			const decoded = atob(content);
			if (decoded.startsWith('data:')) {
				const base64Index = decoded.indexOf(',');
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
			console.log(`Processing file: ${file.name}`);

			// Convert file to base64
			const base64Content = await fileToBase64(file);
			const normalizedNewContent = normalizeFileContent(base64Content);

			// Check if file already exists
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
					size: file.size
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
					const messages = error.data.detail.map(err => err.msg || JSON.stringify(err)).join(', ');
					throw new Error(`File validation error: ${messages}`);
				} else if (typeof error.data.detail === 'string') {
					throw new Error(error.data.detail);
				} else {
					throw new Error(`File processing failed: ${JSON.stringify(error.data.detail)}`);
				}
			}

			throw error;
		}
	};

	// Transform initial data to match form field expectations
	const transformInitialData = (data) => {
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
	};

	// Define layout groups for job application fields
	const layoutGroups = [
		{
			id: "application-date-status",
			type: "row",
			fields: [
				{
					name: "date",
					label: "Application Date",
					type: "datetime-local",
					required: true,
					columnClass: "col-md-6",
					placeholder: "Select application date and time",
				},
				{
					name: "status",
					label: "Application Status",
					type: "select",
					options: [
						{ value: "Applied", label: "Applied" },
						{ value: "Interview", label: "Interview" },
						{ value: "Rejected", label: "Rejected" },
						{ value: "Offer", label: "Offer" },
						{ value: "Withdrawn", label: "Withdrawn" },
					],
					required: true,
					columnClass: "col-md-6",
				},
			],
		},
		{
			id: "application-url",
			type: "default",
			fields: [
				{
					name: "url",
					label: "Application URL",
					type: "text",
					placeholder: "https://... (link to your application submission)",
				},
			],
		},
		{
			id: "application-note",
			type: "default",
			fields: [
				{
					name: "note",
					label: "Application Notes",
					type: "textarea",
					placeholder: "Add notes about your application process, interview details, etc...",
				},
			],
		},
		{
			id: "application-files",
			type: "row",
			fields: [
				{
					name: "cv",
					label: "CV/Resume",
					type: "drag-drop",
					columnClass: "col-md-6",
					handleFileDownload: handleFileDownload,
				},
				{
					name: "cover_letter",
					label: "Cover Letter",
					type: "drag-drop",
					columnClass: "col-md-6",
					handleFileDownload: handleFileDownload,
				},
			],
		},
	];

	// Custom submit handler to process files before form submission
	const handleCustomSubmit = async (formElement, submitCallback) => {
		console.log("Processing files from form submission...");

		try {
			// Get form data from the actual form element
			const formData = new FormData(formElement);
			const transformedData = {};

			// Process all form fields
			for (const [key, value] of formData.entries()) {
				if (value instanceof File && value.size > 0) {
					// Process file and get ID
					console.log(`Processing file field: ${key}`);
					try {
						const fileId = await processFile(value);

						// Convert field name from 'cv' to 'cv_id', 'cover_letter' to 'cover_letter_id'
						const idFieldName = `${key}_id`;
						transformedData[idFieldName] = fileId;
					} catch (fileError) {
						console.error(`Error processing file ${key}:`, fileError);
						throw new Error(`Failed to process ${key}: ${fileError.message}`);
					}
				} else if (typeof value === 'string') {
					// Regular form field
					transformedData[key] = value;
				}
			}

			console.log("Files processed successfully, submitting form...", transformedData);

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
		console.log("Final form data transformation:", data);

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

		// Clean up empty values but preserve legitimate empty strings
		const cleanedData = Object.fromEntries(
			Object.entries(transformed).filter(([key, value]) => {
				if (value === null || value === undefined) return false;
				// Allow empty strings for url and note fields
				if (typeof value === 'string' && value === '' && key !== 'url' && key !== 'note') return false;
				return true;
			})
		);

		console.log("Final transformed data:", cleanedData);
		return cleanedData;
	};

	// Prepare initial data for the form
	const preparedInitialData = transformInitialData(initialData);

	return (
		<>
			<GenericModal
				ref={formRef}
				show={show}
				onHide={onHide}
				mode="form"
				title="Job Application"
				size={size}
				useCustomLayout={true}
				layoutGroups={layoutGroups}
				initialData={preparedInitialData}
				transformFormData={transformFormData}
				endpoint="jobapplications"
				onSuccess={onSuccess}
				isEdit={isEdit}
				customSubmitHandler={handleCustomSubmit} // Pass custom submit handler
			/>

			{/* Alert Modal for error messages */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};

export default JobApplicationFormModal;