import React, { useRef, useState, JSX } from "react";
import { createPortal } from "react-dom";
import { useAuth } from "../../../contexts/AuthContext";
import { filesApi } from "../../../services/api/DataTables";
import { FileData, FileMetadataData } from "../../../services/schemas/DataTables";
import { canPreviewFile, fileToBase64, formatFileSize } from "../../../utils/FileUtils";
import { WidgetProps } from "./WidgetRenders";
import "./FileUploadWidget.scss";
import { ApiResponse } from "../../../services/api/Base";
import { Button } from "react-bootstrap";

export const FileUploadWidget = ({ field, value, handleChange, data, onUploadingChange }: WidgetProps): JSX.Element => {
	const { token } = useAuth();
	const fileInputRef = useRef<HTMLInputElement>(null);
	const tooltipRef = useRef<HTMLDivElement>(null);
	const [uploading, setUploading] = useState<boolean>(false);
	const [uploadError, setUploadError] = useState<string | null>(null);
	const [dragOver, setDragOver] = useState<boolean>(false);
	const [tooltipCoords, setTooltipCoords] = useState<{ top: number; left: number } | null>(null);

	const metadataKey = field.name === "cv_id" ? "application_cv" : "application_cover_letter";
	const fileType = field.fileType ?? null;
	const fileMetadata: FileMetadataData | null = value ? (data?.[metadataKey] ?? null) : null;

	const uploadFile = async (file: File): Promise<void> => {
		if (!token) return;
		setUploading(true);
		onUploadingChange?.(true);
		setUploadError(null);
		try {
			const content: string | ArrayBuffer | null = await fileToBase64(file);
			const result: ApiResponse<FileData> = await filesApi.create(
				{
					filename: file.name,
					content,
					type: file.type || "application/octet-stream",
					size: file.size,
					file_type: fileType,
				},
				token
			);
			handleChange({ target: { name: field.name as string, value: result.data.id } });
			handleChange({ target: { name: metadataKey, value: result.data } });
		} catch (err: any) {
			setUploadError(err.message || "Upload failed");
		} finally {
			setUploading(false);
			onUploadingChange?.(false);
			if (fileInputRef.current) fileInputRef.current.value = "";
		}
	};

	const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
		const file: File | undefined = e.target.files?.[0];
		if (file) void uploadFile(file);
	};

	const handleDrop = (e: React.DragEvent): void => {
		e.preventDefault();
		setDragOver(false);
		const file: File | undefined = e.dataTransfer.files?.[0];
		if (file) void uploadFile(file);
	};

	const handleDragOver = (e: React.DragEvent): void => {
		e.preventDefault();
		setDragOver(true);
	};

	const handleDragLeave = (): void => setDragOver(false);

	const handleRemove = (): void => {
		handleChange({ target: { name: field.name as string, value: null } });
		handleChange({ target: { name: metadataKey, value: null } });
	};

	const handleDownload = async (): Promise<void> => {
		if (!value || !fileMetadata || !token) return;
		await filesApi.download(value, fileMetadata.filename, token);
	};

	const handlePreview = async (): Promise<void> => {
		if (!value || !fileMetadata || !token || !canPreviewFile(fileMetadata.type)) return;
		await filesApi.preview(value, token);
	};

	const handleTooltipEnter = (): void => {
		if (!tooltipRef.current) return;
		const rect = tooltipRef.current.getBoundingClientRect();
		setTooltipCoords({ top: rect.top - 8, left: rect.left + rect.width / 2 });
	};

	const handleTooltipLeave = (): void => setTooltipCoords(null);

	const hasFile: boolean = !!value && !!fileMetadata;

	return (
		<div>
			<input ref={fileInputRef} type="file" className="d-none" onChange={handleInputChange} />
			<div
				className={`file-drop-zone${dragOver ? " drag-over" : ""}${uploading ? " uploading" : ""}${hasFile ? " has-file" : ""}`}
				onClick={() => !uploading && !hasFile && fileInputRef.current?.click()}
				onDrop={handleDrop}
				onDragOver={handleDragOver}
				onDragLeave={handleDragLeave}
			>
				{uploading ? (
					<>
						<div className="file-drop-icon">
							<span className="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
						</div>
						<div className="file-drop-text">Uploading...</div>
					</>
				) : dragOver ? (
					<>
						<div className="file-drop-icon">
							<i className="bi bi-box-arrow-in-down" />
						</div>
						<div className="file-drop-text">Drop to upload</div>
					</>
				) : hasFile ? (
					<>
						<div className="file-drop-icon">
							<i className="bi bi-file-earmark-check" />
						</div>
						<div className="file-drop-filename">{fileMetadata!.filename}</div>
						<div className="file-drop-filesize text-muted">{formatFileSize(fileMetadata!.size)}</div>
						<div className="file-drop-actions" onClick={(e) => e.stopPropagation()}>
							{canPreviewFile(fileMetadata!.type) ? (
								<Button
									variant={"outline-secondary"}
									className="file-drop-action-btn"
									onClick={handlePreview}
									title="Preview"
								>
									<i className="bi bi-eye" />
								</Button>
							) : (
								<div
									ref={tooltipRef}
									onMouseEnter={handleTooltipEnter}
									onMouseLeave={handleTooltipLeave}
									style={{ cursor: "not-allowed" }}
								>
									<Button
										variant={"outline-secondary"}
										className="file-drop-action-btn"
										disabled
										style={{ pointerEvents: "none" }}
									>
										<i className="bi bi-eye" />
									</Button>
								</div>
							)}
							<Button
								variant={"outline-primary"}
								className="file-drop-action-btn"
								onClick={handleDownload}
								title="Download"
							>
								<i className="bi bi-download" />
							</Button>
							<Button
								variant={"outline-danger"}
								className="file-drop-action-btn"
								onClick={handleRemove}
								title="Remove"
							>
								<i className="bi bi-x-lg" />
							</Button>
						</div>
						{tooltipCoords &&
							createPortal(
								<div
									className="ab-tooltip-portal ab-tooltip-portal--top"
									style={{ top: tooltipCoords.top, left: tooltipCoords.left }}
								>
									Preview not available for this file type
								</div>,
								document.body
							)}
					</>
				) : (
					<>
						<div className="file-drop-icon">
							<i className="bi bi-cloud-upload" />
						</div>
						<div className="file-drop-text">
							Drag & drop or <span className="file-drop-link">click to select</span>
						</div>
					</>
				)}
			</div>
			{uploadError && <div className="text-danger mt-1 small">{uploadError}</div>}
		</div>
	);
};
