import React, { useCallback, useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import useGenericAlert from "../hooks/useGenericAlert";
import AlertModal from "../components/AlertModal";
import "./FileUtils.css";

export const fileToBase64 = (file) => {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.readAsDataURL(file);
		reader.onload = () => resolve(reader.result);
		reader.onerror = (error) => reject(error);
	});
};

// Helper function to parse size text like "10MB" to bytes
const parseSizeText = (sizeText) => {
	if (!sizeText) return 10 * 1024 * 1024; // Default 10MB

	const match = sizeText.match(/^(\d+(?:\.\d+)?)\s*(KB|MB|GB)$/i);
	if (!match) return 10 * 1024 * 1024; // Default 10MB if invalid format

	const value = parseFloat(match[1]);
	const unit = match[2].toUpperCase();

	switch (unit) {
		case "KB":
			return value * 1024;
		case "MB":
			return value * 1024 * 1024;
		case "GB":
			return value * 1024 * 1024 * 1024;
		default:
			return 10 * 1024 * 1024; // Default 10MB
	}
};

// Helper function to format file size from bytes
const formatFileSize = (bytes) => {
	if (!bytes || bytes === 0) return "";
	if (bytes < 1024) return `${bytes} B`;
	if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
	return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

// Helper function to calculate file size from base64 content
const calculateBase64Size = (base64Content) => {
	if (!base64Content) return 0;

	// Remove data URL prefix if present
	let content = base64Content;
	if (content.includes(",")) {
		content = content.split(",")[1];
	}

	// Calculate approximate size (base64 is ~1.33x larger than original)
	const base64Length = content.length;
	const padding = (content.match(/=/g) || []).length;
	return Math.floor((base64Length * 3) / 4) - padding;
};

const FileUploader = ({
	fieldName,
	label,
	value,
	onChange,
	error,
	validateFile,
	onOpenFile,
	onRemoveFile,
	acceptedFileTypes = ".txt, .pdf, .doc, .docx",
	maxSizeText = "10MB",
}) => {
	const [file, setFile] = useState(null);
	const [downloadUrl, setDownloadUrl] = useState("");
	const { alertState, showError, hideAlert } = useGenericAlert();

	// Parse max size from text
	const maxSizeBytes = parseSizeText(maxSizeText);

	// Initialize file from value prop
	useEffect(() => {
		if (value && value instanceof File) {
			setFile(value);
		} else if (value && typeof value === "object" && value.filename) {
			setFile(value);
		} else {
			setFile(null);
		}
	}, [value]);

	// Create download URL for new files
	useEffect(() => {
		if (file && file instanceof File) {
			const url = URL.createObjectURL(file);
			setDownloadUrl(url);
			return () => URL.revokeObjectURL(url);
		} else {
			setDownloadUrl("");
		}
	}, [file]);

	// Show error using custom modal
	const showFileError = (message) => {
		showError({
			title: "File Upload Error",
			message: message,
			size: "md",
		});
	};

	// Built-in validation for file size and type
	const validateFileInternal = (file) => {
		// Check file size
		if (file.size > maxSizeBytes) {
			return {
				valid: false,
				error: `File size must be less than ${maxSizeText}. Current file is ${(file.size / (1024 * 1024)).toFixed(2)}MB.`,
			};
		}

		// Check file type if acceptedFileTypes is provided
		if (acceptedFileTypes) {
			const extensions = acceptedFileTypes.split(",").map((ext) => ext.trim().toLowerCase());
			const fileName = file.name.toLowerCase();
			const isValidType = extensions.some((ext) => fileName.endsWith(ext.replace(".", "")));

			if (!isValidType) {
				return {
					valid: false,
					error: `Please upload a file with one of these extensions: ${acceptedFileTypes}`,
				};
			}
		}

		return { valid: true };
	};

	const onDrop = useCallback(
		(acceptedFiles) => {
			if (acceptedFiles.length > 0) {
				const droppedFile = acceptedFiles[0];

				// First run internal validation
				const internalValidation = validateFileInternal(droppedFile);
				if (!internalValidation.valid) {
					showFileError(internalValidation.error);
					return;
				}

				// Then run custom validation if provided
				if (validateFile) {
					const customValidation = validateFile(droppedFile);
					if (!customValidation.valid) {
						showFileError(customValidation.error);
						return;
					}
				}

				setFile(droppedFile);

				// Trigger onChange for parent component
				if (onChange) {
					const syntheticEvent = {
						target: {
							name: fieldName,
							value: droppedFile,
							files: [droppedFile],
						},
					};
					onChange(syntheticEvent);
				}
			}
		},
		[fieldName, onChange, validateFile, validateFileInternal, showFileError],
	);

	// Handle rejected files (too large, wrong type, etc.)
	const onDropRejected = useCallback(
		(fileRejections) => {
			if (fileRejections.length > 0) {
				const rejection = fileRejections[0];
				const file = rejection.file;
				const errors = rejection.errors;

				// Find the most relevant error
				const sizeError = errors.find((err) => err.code === "file-too-large");
				const typeError = errors.find((err) => err.code === "file-invalid-type");

				if (sizeError) {
					showFileError(
						`File size must be less than ${maxSizeText}. Current file is ${(file.size / (1024 * 1024)).toFixed(2)}MB.`,
					);
				} else if (typeError) {
					showFileError(`Please upload a file with one of these extensions: ${acceptedFileTypes}`);
				} else {
					// Generic error message
					showFileError(errors[0]?.message || "File upload failed");
				}
			}
		},
		[maxSizeText, acceptedFileTypes, showFileError],
	);

	const removeFile = () => {
		setFile(null);
		setDownloadUrl("");

		if (onRemoveFile) {
			onRemoveFile(fieldName, onChange);
		} else if (onChange) {
			const syntheticEvent = {
				target: {
					name: fieldName,
					value: null,
				},
			};
			onChange(syntheticEvent);
		}
	};

	const handleDownload = () => {
		if (file && file instanceof File && downloadUrl) {
			const link = document.createElement("a");
			link.href = downloadUrl;
			link.download = file.name;
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
		} else if (file && file.filename && onOpenFile) {
			onOpenFile(file);
		}
	};

	// Get file size for display
	const getFileSize = () => {
		if (file && file instanceof File) {
			// New file - use File.size
			return formatFileSize(file.size);
		} else if (file && file.content) {
			// Database file - calculate from base64 content
			const size = calculateBase64Size(file.content);
			return formatFileSize(size);
		} else if (file && file.size) {
			// Database file with size property
			return formatFileSize(file.size);
		}
		return "";
	};

	const { getRootProps, getInputProps, isDragActive } = useDropzone({
		onDrop,
		onDropRejected,
		multiple: false,
		maxSize: maxSizeBytes,
		accept: {
			"application/pdf": [".pdf"],
			"application/msword": [".doc"],
			"application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
			"text/plain": [".txt"],
		},
	});

	const hasNewFile = file && file instanceof File;
	const hasExistingFile = file && typeof file === "object" && file.filename && !file.name;
	const hasFile = hasNewFile || hasExistingFile;
	const fileSize = getFileSize();

	return (
		<>
			<div className="file-uploader-container">
				{label && <label className="form-label">{label}</label>}

				<div
					{...getRootProps()}
					className={`file-dropzone ${isDragActive ? "drag-active" : ""} ${hasFile ? "has-file" : ""} ${error ? "is-invalid" : ""}`}
				>
					<input {...getInputProps()} />

					{!hasFile && (
						<div className="dropzone-content">
							<i
								className={`bi ${isDragActive ? "bi-cloud-arrow-down" : "bi-cloud-arrow-up"} dropzone-icon`}
							></i>
							<div className="dropzone-text">Drag & drop your file here</div>
							<div className="dropzone-text">Or click to select a file</div>
							<div className="dropzone-info">
								Max size: {maxSizeText} • {acceptedFileTypes.replace(/\./g, "").toUpperCase()}
							</div>
						</div>
					)}

					{hasFile && (
						<div className="file-card">
							<div className="file-info">
								<i className={`bi bi-file-earmark-text file-icon`}></i>
								<div className="file-details">
									<div className="file-name">{hasNewFile ? file.name : file.filename}</div>
									{fileSize && <small className="file-size text-muted">{fileSize}</small>}
								</div>
							</div>

							<div className="file-actions">
								<button
									type="button"
									className="btn-file-action btn-file-download"
									onClick={(e) => {
										e.stopPropagation();
										handleDownload();
									}}
									title={hasNewFile ? "Download file" : "Open file"}
								>
									<i className="bi bi-download"></i>
								</button>

								<button
									type="button"
									className="btn-file-action btn-file-remove"
									onClick={(e) => {
										e.stopPropagation();
										removeFile();
									}}
									title="Remove file"
								>
									<i className="bi bi-trash"></i>
								</button>
							</div>
						</div>
					)}
				</div>

				{error && <div className="invalid-feedback d-block mt-1">{error}</div>}
			</div>

			{/* Alert Modal for file upload errors */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};

export default FileUploader;
