import React, { useMemo } from "react";
import GenericModal from "../GenericModal";
import { getCurrentDateTime } from "../../utils/TimeUtils";
import { fileToBase64 } from "../../utils/FileUtils";
import FileUploader from "../../utils/FileUtils";

const JobApplicationFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false, jobId }) => {
	const currentDateTime = getCurrentDateTime();

	// Prepare initial data with defaults and clean values
	const preparedInitialData = useMemo(() => {
		const cleanedData = {
			status: "Applied",
			date: currentDateTime,
			url: "",
			note: "",
			...initialData,
		};

		if (isEdit && initialData.id) {
			cleanedData.id = initialData.id;
		}

		Object.keys(cleanedData).forEach((key) => {
			if (cleanedData[key] === null || cleanedData[key] === undefined) {
				if (key === "date") {
					cleanedData[key] = currentDateTime;
				} else if (key === "status") {
					cleanedData[key] = "Applied";
				} else if (key === "url" || key === "note") {
					cleanedData[key] = "";
				} else if (!["cv", "cover_letter", "id"].includes(key)) {
					delete cleanedData[key];
				}
			}
		});

		if (initialData.cv && typeof initialData.cv === "object" && initialData.cv.filename) {
			cleanedData.cv = initialData.cv;
		} else {
			delete cleanedData.cv;
		}

		if (
			initialData.cover_letter &&
			typeof initialData.cover_letter === "object" &&
			initialData.cover_letter.filename
		) {
			cleanedData.cover_letter = initialData.cover_letter;
		} else {
			delete cleanedData.cover_letter;
		}

		if (typeof cleanedData.url !== "string") cleanedData.url = "";
		if (typeof cleanedData.note !== "string") cleanedData.note = "";
		if (!cleanedData.status) cleanedData.status = "Applied";
		if (!cleanedData.date) cleanedData.date = currentDateTime;

		return cleanedData;
	}, [initialData, currentDateTime, isEdit]);

	// Validate file type and size
	const validateFile = (file) => {
		const allowedTypes = [
			"application/pdf",
			"application/msword",
			"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
		];
		const maxSize = 10 * 1024 * 1024; // 10MB

		if (!allowedTypes.includes(file.type)) {
			return { valid: false, error: "Please upload a PDF, DOC, or DOCX file" };
		}
		if (file.size > maxSize) {
			return { valid: false, error: "File size must be less than 10MB" };
		}
		return { valid: true };
	};

	const handleOpenFile = (fileData) => {
		if (!fileData?.content) {
			alert("No file content available");
			return;
		}

		if (typeof fileData.content === "string") {
			try {
				let base64Content = fileData.content;
				if (base64Content.includes(",")) {
					base64Content = base64Content.split(",")[1];
				}

				const binaryString = atob(base64Content);
				const bytes = new Uint8Array(binaryString.length);
				for (let i = 0; i < binaryString.length; i++) {
					bytes[i] = binaryString.charCodeAt(i);
				}

				const blob = new Blob([bytes], {
					type: fileData.type || "application/octet-stream",
				});

				if (blob.size === 0) {
					alert("File is empty (0 bytes)");
					return;
				}

				const url = window.URL.createObjectURL(blob);
				const link = document.createElement("a");
				link.href = url;
				link.download = fileData.filename || "document";
				document.body.appendChild(link);
				link.click();
				document.body.removeChild(link);
				window.URL.revokeObjectURL(url);
				return;
			} catch (error) {
				console.error("Error processing base64 content:", error);
				alert("Error opening file: " + error.message);
				return;
			}
		}

		if (typeof fileData.content !== "string") {
			try {
				const blob = new Blob([fileData.content], {
					type: fileData.type || "application/pdf",
				});

				if (blob.size === 0) {
					alert("File is empty (0 bytes)");
					return;
				}

				const url = window.URL.createObjectURL(blob);
				const link = document.createElement("a");
				link.href = url;
				link.download = fileData.filename || "document.pdf";
				document.body.appendChild(link);
				link.click();
				document.body.removeChild(link);
				window.URL.revokeObjectURL(url);
				return;
			} catch (binaryError) {
				console.error("Binary data processing failed:", binaryError);
			}
		}

		alert("Unable to process file. Check console for details.");
	};

	const handleRemoveFile = (fieldName, onChange) => {
		onChange({ target: { name: fieldName, value: null } });
	};

	// Create a wrapper for the FileUploader component
	const FileUploaderWrapper = ({ fieldName, label, value, onChange, error }) => {
		return (
			<FileUploader
				fieldName={fieldName}
				label={label}
				value={value}
				onChange={onChange}
				error={error}
				validateFile={validateFile}
				onOpenFile={handleOpenFile}
				onRemoveFile={handleRemoveFile}
			/>
		);
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
					rows: 3,
					placeholder: "Add notes about your application process, interview details, etc...",
				},
			],
		},
		{
			id: "files-header",
			type: "custom",
			className: "mt-4 mb-3",
			content: (
				<div className="border-top pt-3">
					<h6 className="mb-0">
						<i className="bi bi-paperclip me-2"></i>
						Application Documents
					</h6>
					<small className="text-muted">Upload your CV and cover letter</small>
				</div>
			),
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

	// Custom validation rules for application fields
	const validationRules = {
		date: (value) => {
			if (value) {
				const selectedDate = new Date(value);
				const now = new Date();
				if (selectedDate > now) {
					return {
						isValid: false,
						message: "Application date cannot be in the future",
					};
				}
			}
			return { isValid: true };
		},
		cv: (value) => {
			if (value && value.size > 10 * 1024 * 1024) {
				return {
					isValid: false,
					message: "CV file size must be less than 10MB",
				};
			}
			return { isValid: true };
		},
		cover_letter: (value) => {
			if (value && value.size > 10 * 1024 * 1024) {
				return {
					isValid: false,
					message: "Cover letter file size must be less than 10MB",
				};
			}
			return { isValid: true };
		},
	};

	// Transform form data before submission
	const transformFormData = async (data) => {
		const transformed = { ...data };

		if (transformed.date) {
			transformed.date = new Date(transformed.date).toISOString();
		}

		if (!transformed.status) {
			transformed.status = "Applied";
		}

		if (jobId) {
			transformed.job_id = jobId;
		}

		if (transformed.url && !transformed.url.trim()) {
			delete transformed.url;
		}
		if (transformed.note && !transformed.note.trim()) {
			delete transformed.note;
		}

		// Handle file fields
		if (transformed.cv && transformed.cv instanceof File) {
			try {
				transformed.cv = await fileToBase64(transformed.cv);
			} catch (error) {
				console.error("Error converting CV to base64:", error);
				delete transformed.cv;
			}
		} else if (
			!transformed.cv ||
			transformed.cv === "" ||
			transformed.cv === null ||
			(typeof transformed.cv === "object" && !transformed.cv.filename)
		) {
			delete transformed.cv;
		}

		if (transformed.cover_letter && transformed.cover_letter instanceof File) {
			try {
				transformed.cover_letter = await fileToBase64(transformed.cover_letter);
			} catch (error) {
				console.error("Error converting cover letter to base64:", error);
				delete transformed.cover_letter;
			}
		} else if (
			!transformed.cover_letter ||
			transformed.cover_letter === "" ||
			transformed.cover_letter === null ||
			(typeof transformed.cover_letter === "object" && !transformed.cover_letter.filename)
		) {
			delete transformed.cover_letter;
		}

		return transformed;
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="form"
			title={isEdit ? "Edit Job Application" : "New Job Application"}
			size={size}
			useCustomLayout={true}
			layoutGroups={layoutGroups}
			initialData={preparedInitialData}
			endpoint="jobapplications"
			onSuccess={onSuccess}
			validationRules={validationRules}
			transformFormData={transformFormData}
			isEdit={isEdit}
			customFieldComponents={{ "drag-drop": FileUploaderWrapper }}
		/>
	);
};

export default JobApplicationFormModal;
