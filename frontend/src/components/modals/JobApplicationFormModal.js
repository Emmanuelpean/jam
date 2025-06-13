import React, { useCallback, useMemo, useState } from "react";
import { Button, Form } from "react-bootstrap";
import GenericModal from "../GenericModal";
import { getCurrentDateTime } from "../../utils/TimeUtils";
import {fileToBase64} from "../../utils/FileUtils";

const JobApplicationFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false, jobId }) => {
	const [dragStates, setDragStates] = useState({ cv: false, cover_letter: false });

	const currentDateTime = getCurrentDateTime();

	// Prepare initial data with defaults and clean values
	const preparedInitialData = useMemo(() => {
		const cleanedData = {
			status: "Applied", // Default status
			date: currentDateTime, // Set to current time when modal opens
			url: "", // Ensure string value
			note: "", // Ensure string value
			...initialData, // Override with any provided initial data
		};

		// Clean up any null/undefined values that could cause form issues
		Object.keys(cleanedData).forEach((key) => {
			if (cleanedData[key] === null || cleanedData[key] === undefined) {
				if (key === "date") {
					cleanedData[key] = currentDateTime;
				} else if (key === "status") {
					cleanedData[key] = "Applied";
				} else if (typeof cleanedData[key] === "string" || key === "url" || key === "note") {
					cleanedData[key] = "";
				} else {
					delete cleanedData[key]; // Remove file fields and other non-string fields
				}
			}
		});

		// Keep file fields if they exist in initial data (for edit mode)
		if (initialData.cv && typeof initialData.cv === 'object' && initialData.cv.filename) {
			cleanedData.cv = initialData.cv;
		} else {
			delete cleanedData.cv;
		}

		if (initialData.cover_letter && typeof initialData.cover_letter === 'object' && initialData.cover_letter.filename) {
			cleanedData.cover_letter = initialData.cover_letter;
		} else {
			delete cleanedData.cover_letter;
		}

		return cleanedData;
	}, [initialData, currentDateTime]);

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

	// Helper function to open/download a file
	const handleOpenFile = (fileData) => {
		if (fileData && fileData.content) {
			try {
				// Convert bytes to blob
				const byteArray = new Uint8Array(fileData.content);
				const blob = new Blob([byteArray], { type: fileData.type || 'application/pdf' });

				// Create download link
				const url = window.URL.createObjectURL(blob);
				const link = document.createElement('a');
				link.href = url;
				link.download = fileData.filename || 'document';
				document.body.appendChild(link);
				link.click();
				document.body.removeChild(link);
				window.URL.revokeObjectURL(url);
			} catch (error) {
				console.error('Error opening file:', error);
				// Fallback: try to open as base64 if the content is base64 encoded
				try {
					const base64Data = fileData.content;
					const byteCharacters = atob(base64Data.split(',')[1] || base64Data);
					const byteNumbers = new Array(byteCharacters.length);
					for (let i = 0; i < byteCharacters.length; i++) {
						byteNumbers[i] = byteCharacters.charCodeAt(i);
					}
					const byteArray = new Uint8Array(byteNumbers);
					const blob = new Blob([byteArray], { type: fileData.type || 'application/pdf' });

					const url = window.URL.createObjectURL(blob);
					const link = document.createElement('a');
					link.href = url;
					link.download = fileData.filename || 'document';
					document.body.appendChild(link);
					link.click();
					document.body.removeChild(link);
					window.URL.revokeObjectURL(url);
				} catch (fallbackError) {
					console.error('Failed to open file with fallback method:', fallbackError);
				}
			}
		}
	};

	// Helper function to remove a file
	const handleRemoveFile = (fieldName, onChange) => {
		onChange({ target: { name: fieldName, value: null } });
	};

	// Create drag and drop component
	const DragDropFile = ({ fieldName, label, value, onChange, error }) => {
		const handleDragEnter = useCallback(
			(e) => {
				e.preventDefault();
				setDragStates((prev) => ({ ...prev, [fieldName]: true }));
			},
			[fieldName],
		);

		const handleDragLeave = useCallback(
			(e) => {
				e.preventDefault();
				if (!e.currentTarget.contains(e.relatedTarget)) {
					setDragStates((prev) => ({ ...prev, [fieldName]: false }));
				}
			},
			[fieldName],
		);

		const handleDragOver = useCallback((e) => {
			e.preventDefault();
		}, []);

		const handleDrop = useCallback(
			(e) => {
				e.preventDefault();
				setDragStates((prev) => ({ ...prev, [fieldName]: false }));

				const files = Array.from(e.dataTransfer.files);
				if (files.length > 0) {
					const file = files[0];
					const validation = validateFile(file);
					if (validation.valid) {
						onChange({ target: { name: fieldName, files: [file] } });
					} else {
						// You might want to show this error somewhere
						console.error(validation.error);
					}
				}
			},
			[fieldName, onChange],
		);

		const handleFileSelect = useCallback(
			(e) => {
				const file = e.target.files[0];
				if (file) {
					const validation = validateFile(file);
					if (validation.valid) {
						onChange(e);
					} else {
						// Clear the input and show error
						e.target.value = "";
						console.error(validation.error);
					}
				}
			},
			[onChange],
		);

		const isDragging = dragStates[fieldName];

		// Check if we have a new file (File object) or existing file (database object)
		const hasNewFile = value && value instanceof File;
		const hasExistingFile = value && typeof value === 'object' && value.filename && !value.name;
		const hasFile = hasNewFile || hasExistingFile;

		return (
			<div>
				<Form.Label>{label}</Form.Label>
				<div
					className={`drag-drop-zone ${isDragging ? "dragging" : ""} ${hasFile ? "has-file" : ""} ${error ? "is-invalid" : ""}`}
					onDragEnter={handleDragEnter}
					onDragLeave={handleDragLeave}
					onDragOver={handleDragOver}
					onDrop={handleDrop}
					style={{
						border: `2px dashed ${error ? "#dc3545" : isDragging ? "#0d6efd" : "#dee2e6"}`,
						borderRadius: "0.375rem",
						padding: "2rem 1rem",
						textAlign: "center",
						backgroundColor: isDragging ? "#f8f9fa" : hasFile ? "#e8f5e8" : "#fafafa",
						cursor: "pointer",
						transition: "all 0.2s ease",
						minHeight: "120px",
						display: "flex",
						flexDirection: "column",
						justifyContent: "center",
						alignItems: "center",
						position: "relative",
					}}
					onClick={() => document.getElementById(`${fieldName}-input`).click()}
				>
					<input
						id={`${fieldName}-input`}
						type="file"
						name={fieldName}
						accept=".pdf,.doc,.docx"
						onChange={handleFileSelect}
						style={{ display: "none" }}
					/>

					{/* Remove button - positioned at top right */}
					{hasFile && (
						<Button
							variant="outline-danger"
							size="sm"
							className="position-absolute"
							style={{ top: "8px", right: "8px", zIndex: 1 }}
							onClick={(e) => {
								e.stopPropagation();
								handleRemoveFile(fieldName, onChange);
							}}
							title="Remove file"
						>
							<i className="bi bi-x"></i>
						</Button>
					)}

					{hasNewFile ? (
						<>
							<i className="bi bi-check-circle-fill text-success mb-2" style={{ fontSize: "2rem" }}></i>
							<div className="fw-semibold text-success">{value.name}</div>
							<small className="text-muted">{(value.size / 1024 / 1024).toFixed(2)} MB</small>
							<small className="text-muted mt-1">Click to replace</small>
						</>
					) : hasExistingFile ? (
						<>
							<i className="bi bi-file-earmark-text text-info mb-2" style={{ fontSize: "2rem" }}></i>
							<div className="fw-semibold text-info mb-2">{value.filename}</div>
							<Button
								variant="outline-info"
								size="sm"
								className="mb-2"
								onClick={(e) => {
									e.stopPropagation();
									handleOpenFile(value);
								}}
							>
								<i className="bi bi-download me-1"></i>
								Open File
							</Button>
							<small className="text-muted">Click anywhere to replace</small>
						</>
					) : isDragging ? (
						<>
							<i className="bi bi-cloud-arrow-down text-primary mb-2" style={{ fontSize: "2rem" }}></i>
							<div className="fw-semibold text-primary">Drop your file here</div>
						</>
					) : (
						<>
							<i className="bi bi-cloud-arrow-up text-muted mb-2" style={{ fontSize: "2rem" }}></i>
							<div className="fw-semibold text-muted mb-1">
								Drag & drop your {label.toLowerCase()} here
							</div>
							<div className="text-muted mb-2">or</div>
							<Button variant="outline-primary" size="sm">
								<i className="bi bi-folder2-open me-1"></i>
								Browse Files
							</Button>
							<small className="text-muted mt-2">PDF, DOC, DOCX up to 10MB</small>
						</>
					)}
				</div>
				{error && <div className="invalid-feedback d-block mt-1">{error}</div>}
			</div>
		);
	};

	// Define layout groups for job application fields
	const layoutGroups = [
		// Application Date and Status
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
		// Application URL
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
		// Application Note
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
		// File Uploads Section
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
					<small className="text-muted">Upload your CV and cover letter by dragging and dropping</small>
				</div>
			),
		},
		// File uploads (side by side) - now using custom drag and drop
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
				// 10MB limit
				return {
					isValid: false,
					message: "CV file size must be less than 10MB",
				};
			}
			return { isValid: true };
		},
		cover_letter: (value) => {
			if (value && value.size > 10 * 1024 * 1024) {
				// 10MB limit
				return {
					isValid: false,
					message: "Cover letter file size must be less than 10MB",
				};
			}
			return { isValid: true };
		},
	};

	// Transform form data before submission
	// Modify the transformFormData function
	const transformFormData = async (data) => {
		const transformed = { ...data };

		// Convert date to ISO string for backend
		if (transformed.date) {
			transformed.date = new Date(transformed.date).toISOString();
		}

		// Set default status if not provided
		if (!transformed.status) {
			transformed.status = "Applied";
		}

		// Add job_id if provided (for creating new applications)
		if (jobId) {
			transformed.job_id = jobId;
		}

		// Clean up empty string values - convert to null for backend
		if (transformed.url && !transformed.url.trim()) {
			delete transformed.url;
		}
		if (transformed.note && !transformed.note.trim()) {
			delete transformed.note;
		}

		// Handle file fields - convert to base64 for database storage
		if (transformed.cv && transformed.cv instanceof File) {
			try {
				transformed.cv = await fileToBase64(transformed.cv);
			} catch (error) {
				console.error('Error converting CV to base64:', error);
				delete transformed.cv;
			}
		} else if (!transformed.cv || transformed.cv === "" || transformed.cv === null || (typeof transformed.cv === 'object' && !transformed.cv.filename)) {
			delete transformed.cv;
		}

		if (transformed.cover_letter && transformed.cover_letter instanceof File) {
			try {
				transformed.cover_letter = await fileToBase64(transformed.cover_letter);
			} catch (error) {
				console.error('Error converting cover letter to base64:', error);
				delete transformed.cover_letter;
			}
		} else if (!transformed.cover_letter || transformed.cover_letter === "" || transformed.cover_letter === null || (typeof transformed.cover_letter === 'object' && !transformed.cover_letter.filename)) {
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
			customFieldComponents={{ "drag-drop": DragDropFile }}
		/>
	);
};

export default JobApplicationFormModal;