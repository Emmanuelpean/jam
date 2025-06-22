import React, { useMemo } from "react";
import { useDropzone } from "react-dropzone";
import useGenericAlert from "../hooks/useGenericAlert";
import AlertModal from "../components/modals/alert/AlertModal";
import "./FileUtils.css";

const formatFileSize = (bytes) => {
	if (!bytes || bytes === 0) return "";
	if (bytes < 1024) return `${bytes} B`;
	if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
	return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const parseSizeText = (sizeText) => {
	const defaultSize = 10 * 1024 * 1024; // 10MB
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

const FileUploader = ({
	name,
	label,
	value,
	onChange,
	onRemove,
	onOpenFile,
	acceptedFileTypes = ".TXT,.PDF,.DOC,.DOCX",
	maxSizeText = "10 MB",
	required = false,
}) => {
	const { alertState, showError, hideAlert } = useGenericAlert();
	const maxSizeBytes = useMemo(() => parseSizeText(maxSizeText), [maxSizeText]);

	// Convert acceptedFileTypes to proper MIME types for react-dropzone
	const acceptTypes = useMemo(() => {
		const extensions = acceptedFileTypes.split(",").map((ext) => ext.trim().toLowerCase());
		const mimeTypes = {};

		extensions.forEach((ext) => {
			switch (ext) {
				case ".pdf":
					mimeTypes["application/pdf"] = [".pdf"];
					break;
				case ".doc":
					mimeTypes["application/msword"] = [".doc"];
					break;
				case ".docx":
					mimeTypes["application/vnd.openxmlformats-officedocument.wordprocessingml.document"] = [".docx"];
					break;
				case ".txt":
					mimeTypes["text/plain"] = [".txt"];
					break;
				case ".jpg":
				case ".jpeg":
					mimeTypes["image/jpeg"] = [".jpg", ".jpeg"];
					break;
				case ".png":
					mimeTypes["image/png"] = [".png"];
					break;
				default:
					mimeTypes[`*/*`] = extensions; // Fallback
			}
		});

		return mimeTypes;
	}, [acceptedFileTypes]);

	const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
		accept: acceptTypes,
		maxSize: maxSizeBytes,
		multiple: false,
		onDrop: (acceptedFiles) => {
			if (acceptedFiles.length > 0 && onChange) {
				onChange(acceptedFiles[0]);
			}
		},
		onDropRejected: (rejections) => {
			// Handle errors with custom error modal
			if (rejections.length > 0) {
				const rejection = rejections[0];
				const file = rejection.file;
				const errors = rejection.errors;

				// Find the most relevant error
				const sizeError = errors.find((err) => err.code === "file-too-large");
				const typeError = errors.find((err) => err.code === "file-invalid-type");

				if (sizeError) {
					showError({
						title: "File Upload Error",
						message: `File size must be less than ${maxSizeText}. Current file is ${formatFileSize(file.size)}.`,
						size: "md",
					});
				} else if (typeError) {
					showError({
						title: "File Upload Error",
						message: `Please upload a file with one of these extensions: ${acceptedFileTypes}`,
						size: "md",
					});
				} else {
					showError({
						title: "File Upload Error",
						message: errors[0]?.message || "File upload failed",
						size: "md",
					});
				}
			}
		},
	});

	const hasFile = value && (value instanceof File || (typeof value === "object" && value.filename));
	const fileName = value?.name || value?.filename || "";
	const fileSize = value?.size ? formatFileSize(value.size) : "";

	const handleRemove = (e) => {
		e.stopPropagation();
		if (onRemove) {
			onRemove();
		}
	};

	const handleDownload = (e) => {
		e.stopPropagation();
		if (value instanceof File) {
			const url = URL.createObjectURL(value);
			const link = document.createElement("a");
			link.href = url;
			link.download = value.name;
			link.click();
			URL.revokeObjectURL(url);
		} else if (onOpenFile && value) {
			onOpenFile(value);
		}
	};

	return (
		<>
			<div className="file-uploader-container">
				{label && (
					<label className="form-label">
						{label}
						{required && <span className="text-danger ms-1">*</span>}
					</label>
				)}

				<div
					{...getRootProps()}
					className={`file-dropzone ${isDragActive ? "drag-active" : ""} ${isDragReject ? "drag-reject" : ""} ${hasFile ? "has-file" : ""}`}
				>
					<input {...getInputProps({ name })} />

					{isDragActive ? (
						<div className="dropzone-content">
							<i className="bi bi-cloud-arrow-down dropzone-icon text-primary"></i>
							<div className="dropzone-text">
								{isDragReject ? "File type not supported" : "Drop your file here"}
							</div>
						</div>
					) : hasFile ? (
						<div className="file-card">
							<div className="file-info">
								<i className="bi bi-file-earmark-text file-icon"></i>
								<div className="file-details">
									<div className="file-name">{fileName}</div>
									{fileSize && <small className="file-size text-muted">{fileSize}</small>}
								</div>
							</div>
							<div className="file-actions">
								<button
									type="button"
									className="btn-file-action btn-file-download"
									onClick={handleDownload}
									title="Download file"
								>
									<i className="bi bi-download"></i>
								</button>
								<button
									type="button"
									className="btn-file-action btn-file-remove"
									onClick={handleRemove}
									title="Remove file"
								>
									<i className="bi bi-trash"></i>
								</button>
							</div>
						</div>
					) : (
						<div className="dropzone-content">
							<i className="bi bi-cloud-arrow-up dropzone-icon"></i>
							<div className="dropzone-text">Drag & drop your file here</div>
							<div className="dropzone-text">Or click to select a file</div>
							<div className="dropzone-info">
								Max size: {maxSizeText} • {acceptedFileTypes.replace(/\./g, "").toUpperCase()}
							</div>
						</div>
					)}
				</div>
			</div>

			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};

export const fileToBase64 = (file) => {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.readAsDataURL(file);
		reader.onload = () => resolve(reader.result);
		reader.onerror = (error) => reject(error);
	});
};

export default FileUploader;
