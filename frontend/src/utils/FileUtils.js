import React, { useCallback, useEffect, useRef, useState } from "react";
import { useDropzone } from "react-dropzone";
import useGenericAlert from "../hooks/useGenericAlert";
import AlertModal from "../components/modals/alert/AlertModal";
import "./FileUtils.css";

export const fileToBase64 = (file) => {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.readAsDataURL(file);
		reader.onload = () => resolve(reader.result);
		reader.onerror = (error) => reject(error);
	});
};

const parseSizeText = (sizeText) => {
	let defaultSize = 10 * 1024 * 1024;

	if (!sizeText) return defaultSize;

	const match = sizeText.match(/^(\d+(?:\.\d+)?)\s*(KB|MB|GB)$/i);
	if (!match) return defaultSize;

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
			return defaultSize;
	}
};

const formatFileSize = (bytes) => {
	if (!bytes || bytes === 0) return "";
	if (bytes < 1024) return `${bytes} B`;
	if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
	return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const getFileType = (file) => {
	if (file && file.path) {
		return "uploaded";
	} else if (file) {
		return "database";
	}
	return "";
};

const parseAcceptedFileTypes = (acceptedFileTypes) => {
	if (!acceptedFileTypes) return {};

	const extensions = acceptedFileTypes.split(",").map((ext) => ext.trim().toLowerCase());
	const acceptObject = {};

	extensions.forEach((ext) => {
		switch (ext) {
			case ".pdf":
				acceptObject["application/pdf"] = [".pdf"];
				break;
			case ".doc":
				acceptObject["application/msword"] = [".doc"];
				break;
			case ".docx":
				acceptObject["application/vnd.openxmlformats-officedocument.wordprocessingml.document"] = [".docx"];
				break;
			case ".txt":
				acceptObject["text/plain"] = [".txt"];
				break;
			case ".jpg":
			case ".jpeg":
				acceptObject["image/jpeg"] = [".jpg", ".jpeg"];
				break;
			case ".png":
				acceptObject["image/png"] = [".png"];
				break;
			case ".gif":
				acceptObject["image/gif"] = [".gif"];
				break;
			case ".csv":
				acceptObject["text/csv"] = [".csv"];
				break;
			case ".xlsx":
				acceptObject["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"] = [".xlsx"];
				break;
			case ".xls":
				acceptObject["application/vnd.ms-excel"] = [".xls"];
				break;
			default:
				// For unknown extensions, create a generic entry
				acceptObject[`application/octet-stream${ext}`] = [ext];
		}
	});

	return acceptObject;
};

const FileUploader = ({
	fieldName,
	label,
	value,
	onChange,
	onRemove,
	error,
	onOpenFile = null,
	onRemoveFile, // Keep this for backward compatibility
	acceptedFileTypes = ".TXT, .PDF, .DOC, .DOCX",
	maxSizeText = "10 MB",
	required = false,
}) => {
	const [downloadUrl, setDownloadUrl] = useState("");
	const { alertState, showError, hideAlert } = useGenericAlert();
	const hiddenInputRef = useRef(null);

	const maxSizeBytes = parseSizeText(maxSizeText);

	// Use controlled value from parent
	const displayFile = value;

	useEffect(() => {
		if (displayFile && displayFile instanceof File) {
			const url = URL.createObjectURL(displayFile);
			setDownloadUrl(url);
			return () => URL.revokeObjectURL(url);
		} else {
			setDownloadUrl("");
		}
	}, [displayFile]);

	const showFileError = (message) => {
		showError({
			title: "File Upload Error",
			message: message,
			size: "md",
		}).then(() => null);
	};

	const updateHiddenInput = (files) => {
		if (hiddenInputRef.current) {
			const dataTransfer = new DataTransfer();
			files.forEach((file) => {
				dataTransfer.items.add(file);
			});
			hiddenInputRef.current.files = dataTransfer.files;
		}
	};

	const onDrop = useCallback(
		(acceptedFiles) => {
			if (acceptedFiles.length > 0) {
				const selectedFile = acceptedFiles[0];

				// Update the hidden input for form submission compatibility
				updateHiddenInput([selectedFile]);

				// Call parent onChange handler
				if (onChange) {
					onChange(selectedFile);
				}
			}
		},
		[onChange],
	);

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
						`File size must be less than ${maxSizeText}. Current file is ${formatFileSize(file.size)}.`,
					);
				} else if (typeError) {
					showFileError(`Please upload a file with one of these extensions: ${acceptedFileTypes}`);
				} else {
					showFileError(errors[0]?.message || "File upload failed");
				}
			}
		},
		[maxSizeText, acceptedFileTypes, showFileError],
	);

	const removeFile = () => {
		// Clear the hidden input
		if (hiddenInputRef.current) {
			hiddenInputRef.current.value = "";
		}

		// Call parent remove handler with proper signature
		if (onRemove) {
			// New controlled component API
			onRemove();
		} else if (onRemoveFile) {
			// Legacy API for backward compatibility
			onRemoveFile(fieldName, onChange);
		} else if (onChange) {
			// Fallback to direct onChange call
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
		const filetype = getFileType(displayFile);
		if (filetype === "uploaded") {
			const link = document.createElement("a");
			link.href = downloadUrl;
			link.download = displayFile.name;
			link.click();
		} else if (filetype === "database" && onOpenFile) {
			onOpenFile(displayFile);
		}
	};

	const canDownload = () => {
		const filetype = getFileType(displayFile);
		if (filetype === "uploaded") {
			return true;
		} else if (filetype === "database" && onOpenFile) {
			return true;
		}
		return false;
	};

	const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
		onDrop: onDrop,
		onDropRejected: onDropRejected,
		multiple: false,
		maxSize: maxSizeBytes,
		accept: parseAcceptedFileTypes(acceptedFileTypes),
		noClick: false, // Allow clicking the entire area
		noKeyboard: false, // Allow keyboard interaction
	});

	const hasNewFile = displayFile && displayFile instanceof File;
	const hasExistingFile = displayFile && typeof displayFile === "object" && displayFile.filename && !displayFile.name;
	const hasFile = hasNewFile || hasExistingFile;
	const fileSize = formatFileSize(displayFile?.size);

	return (
		<>
			<div className="file-uploader-container">
				{label && <label className="form-label">{label}</label>}

				<div
					{...getRootProps()}
					className={`file-dropzone ${isDragActive ? "drag-active" : ""} ${hasFile ? "has-file" : ""} ${error ? "is-invalid" : ""}`}
					style={{ cursor: "pointer" }}
				>
					{/* Hidden file input for form submission compatibility */}
					<input
						type="file"
						name={fieldName}
						required={required}
						style={{ opacity: 0, position: "absolute", pointerEvents: "none" }}
						ref={hiddenInputRef}
						accept={acceptedFileTypes}
					/>

					{/* Dropzone input (hidden) */}
					<input {...getInputProps()} />

					{isDragActive ? (
						<div className="dropzone-content">
							<i className="bi bi-cloud-arrow-down dropzone-icon"></i>
							<div className="dropzone-text">Drop your file here</div>
							<div className="dropzone-info">
								Max size: {maxSizeText} • {acceptedFileTypes.replace(/\./g, "").toUpperCase()}
							</div>
						</div>
					) : !hasFile ? (
						<div className="dropzone-content">
							<i className="bi bi-cloud-arrow-up dropzone-icon"></i>
							<div className="dropzone-text">Drag & drop your file here</div>
							<div className="dropzone-text">Or click to select a file</div>
							<div className="dropzone-info">
								Max size: {maxSizeText} • {acceptedFileTypes.replace(/\./g, "").toUpperCase()}
							</div>
						</div>
					) : (
						<div className="file-card">
							<div className="file-info">
								<i className={`bi bi-file-earmark-text file-icon`}></i>
								<div className="file-details">
									<div className="file-name">
										{hasNewFile ? displayFile.name : displayFile.filename}
									</div>
									{fileSize && <small className="file-size text-muted">{fileSize}</small>}
								</div>
							</div>

							<div className="file-actions">
								{canDownload() && (
									<button
										type="button"
										className="btn-file-action btn-file-download"
										onClick={(e) => {
											e.stopPropagation();
											handleDownload();
										}}
										title="Download file"
									>
										<i className="bi bi-download"></i>
									</button>
								)}

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
