import React, { useCallback, useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import "./FileUtils.css";

export const fileToBase64 = (file) => {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.readAsDataURL(file);
		reader.onload = () => resolve(reader.result);
		reader.onerror = (error) => reject(error);
	});
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
	acceptedFileTypes = ".pdf,.doc,.docx",
	maxSizeText = "10MB",
}) => {
	const [file, setFile] = useState(null);
	const [downloadUrl, setDownloadUrl] = useState("");

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

	const onDrop = useCallback(
		(acceptedFiles) => {
			if (acceptedFiles.length > 0) {
				const droppedFile = acceptedFiles[0];

				if (validateFile) {
					const validation = validateFile(droppedFile);
					if (!validation.valid) {
						alert(validation.error);
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
		[fieldName, onChange, validateFile],
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

	const { getRootProps, getInputProps, isDragActive } = useDropzone({
		onDrop,
		multiple: false,
		accept: {
			"application/pdf": [".pdf"],
			"application/msword": [".doc"],
			"application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
		},
	});

	const hasNewFile = file && file instanceof File;
	const hasExistingFile = file && typeof file === "object" && file.filename && !file.name;
	const hasFile = hasNewFile || hasExistingFile;

	return (
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
						<div className="dropzone-text">
							{isDragActive
								? "Drop your file here…"
								: `Drag & drop your ${(label || "file").toLowerCase()} here`}
						</div>
						{!isDragActive && (
							<>
								<div className="dropzone-or">or</div>
								<button type="button" className="btn btn-outline-primary btn-sm">
									<i className="bi bi-folder2-open me-1"></i>
									Browse Files
								</button>
								<small className="dropzone-info">
									{acceptedFileTypes.replace(/\./g, "").toUpperCase()} up to {maxSizeText}
								</small>
							</>
						)}
					</div>
				)}

				{hasFile && (
					<div className="file-card">
						<div className="file-info">
							<i
								className={`bi ${hasNewFile ? "bi-check-circle-fill text-success" : "bi-file-earmark-text text-info"} file-icon`}
							></i>
							<div className="file-details">
								<div className="file-name" title={hasNewFile ? file.name : file.filename}>
									{hasNewFile ? file.name : file.filename}
								</div>
								{hasNewFile && (
									<small className="file-size text-muted">
										{(file.size / 1024 / 1024).toFixed(2)} MB
									</small>
								)}
							</div>
						</div>

						<div className="file-actions">
							<button
								type="button"
								className="btn btn-outline-info btn-sm me-2"
								onClick={(e) => {
									e.stopPropagation();
									handleDownload();
								}}
								title={hasNewFile ? "Download file" : "Open file"}
							>
								<i className="bi bi-download me-1"></i>
								{hasNewFile ? "Download" : "Open"}
							</button>

							<button
								type="button"
								className="btn btn-outline-danger btn-sm"
								onClick={(e) => {
									e.stopPropagation();
									removeFile();
								}}
								title="Remove file"
							>
								<i className="bi bi-x"></i>
							</button>
						</div>

						<div className="file-replace-hint">
							<small className="text-muted">Click anywhere to replace</small>
						</div>
					</div>
				)}
			</div>

			{error && <div className="invalid-feedback d-block mt-1">{error}</div>}
		</div>
	);
};

export default FileUploader;
