import React from "react";
import GenericModal from "../GenericModal";
import FileUploader from "../../utils/FileUtils";

const JobApplicationFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false, jobId }) => {
	// Add a function to handle file downloads from the database
	const handleFileDownload = async (fileObject) => {
		try {
			// Construct the download URL for the backend
			const downloadUrl = `${process.env.REACT_APP_API_BASE_URL || "http://localhost:8000"}/api/files/${fileObject.id}/download`;

			// Create a temporary link and trigger download
			const link = document.createElement("a");
			link.href = downloadUrl;
			link.download = fileObject.filename;
			link.target = "_blank"; // Open in new tab as fallback
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
		} catch (error) {
			console.error("Error downloading file:", error);
			alert("Error downloading file. Please try again.");
		}
	};

	const FileUploaderWrapper = ({ fieldName, label, value, onChange, error }) => {
		return (
			<FileUploader
				fieldName={fieldName}
				label={label}
				value={value}
				onChange={onChange}
				error={error}
				onOpenFile={handleFileDownload}
			/>
		);
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

		// Handle file fields - keep the file objects for display
		if (transformed.cv && typeof transformed.cv === "object") {
			// Keep the cv object as-is for the file uploader
		}
		if (transformed.cover_letter && typeof transformed.cover_letter === "object") {
			// Keep the cover_letter object as-is for the file uploader
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
				},
				{
					name: "cover_letter",
					label: "Cover Letter",
					type: "drag-drop",
					columnClass: "col-md-6",
				},
			],
		},
	];

	const transformFormData = (data) => {
		console.log("Original form data:", data);
		console.log("Initial data:", initialData);
		console.log("Is edit mode:", isEdit);

		const transformed = { ...data };

		// Convert datetime-local back to ISO format
		if (transformed.date) {
			transformed.date = new Date(transformed.date).toISOString();
		}

		// Add job_id for new applications
		if (!isEdit && jobId) {
			transformed.job_id = jobId;
		}

		// Clean up system fields that shouldn't be sent to backend
		delete transformed.created_at;
		delete transformed.modified_at;
		delete transformed.owner_id;
		delete transformed.cv_id;
		delete transformed.cover_letter_id;
		delete transformed.job;
		delete transformed.interviews;

		console.log("Transformed data for submission:", transformed);
		return transformed;
	};

	// Prepare initial data for the form
	const preparedInitialData = transformInitialData(initialData);

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="form"
			title="Job Application"
			size={size}
			useCustomLayout={true}
			layoutGroups={layoutGroups}
			initialData={preparedInitialData}
			endpoint="jobapplications"
			onSuccess={onSuccess}
			transformFormData={transformFormData}
			isEdit={isEdit}
			customFieldComponents={{ "drag-drop": FileUploaderWrapper }}
		/>
	);
};

export default JobApplicationFormModal;
