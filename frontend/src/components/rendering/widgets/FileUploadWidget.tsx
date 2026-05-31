import React, { useRef, useState, JSX, ReactNode } from "react";
import { createPortal } from "react-dom";
import { useAuth } from "../../../contexts/AuthContext";
import { useConfig } from "../../../contexts/ConfigContext";
import { useDataContext } from "../../../contexts/DataContext";
import { filesApi } from "../../../services/api/DataTables";
import { FileData } from "../../../services/schemas/DataTables";
import { canPreviewFile, fileToBase64, formatFileSize } from "../../../utils/FileUtils";
import { WidgetProps } from "./WidgetRenders";
import "./FileUploadWidget.scss";
import { Button } from "react-bootstrap";

export interface FileUploadWidgetProps extends WidgetProps {
	extraActions?: ReactNode;
}

export const FileUploadWidget = ({
	field,
	value,
	handleChange,
	data,
	onUploadingChange,
	extraActions,
}: FileUploadWidgetProps): JSX.Element => {
	const { token } = useAuth();
	const { config } = useConfig();
	const { addEntity, files } = useDataContext();
	const fileInputRef = useRef<HTMLInputElement>(null);
	const tooltipRef = useRef<HTMLDivElement>(null);
	const [uploading, setUploading] = useState<boolean>(false);
	const [uploadError, setUploadError] = useState<string | null>(null);
	const [dragOver, setDragOver] = useState<boolean>(false);
	const [tooltipCoords, setTooltipCoords] = useState<{ top: number; left: number } | null>(null);

	const fileType = field.fileType ?? null;
	const fileMetadata: FileData | null = value ? (files.find((f) => f.id === value) ?? null) : null;

	const uploadFile = async (file: File): Promise<void> => {
		if (!token) return;
		if (config?.max_file_size_mb) {
			const maxBytes = config.max_file_size_mb * 1024 * 1024;
			if (file.size > maxBytes) {
				setUploadError(`File exceeds the maximum allowed size of ${config.max_file_size_mb} MB.`);
				if (fileInputRef.current) fileInputRef.current.value = "";
				return;
			}
		}
		if (config?.column_limits?.file_name && file.name.length > config.column_limits.file_name) {
			setUploadError(
				`Filename exceeds the maximum allowed length of ${config.column_limits.file_name} characters.`
			);
			if (fileInputRef.current) fileInputRef.current.value = "";
			return;
		}
		if (config?.column_limits?.file_mimetype && file.type.length > config.column_limits.file_mimetype) {
			setUploadError(
				`File type identifier exceeds the maximum allowed length of ${config.column_limits.file_mimetype} characters.`
			);
			if (fileInputRef.current) fileInputRef.current.value = "";
			return;
		}
		setUploading(true);
		onUploadingChange?.(true);
		setUploadError(null);
		try {
			const content: string | ArrayBuffer | null = await fileToBase64(file);
			const result = await addEntity("file", {
				filename: file.name,
				content,
				type: file.type || "application/octet-stream",
				size: file.size,
				file_type: fileType,
			});
			handleChange({ target: { name: field.key as string, value: result.data.id } });
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
		handleChange({ target: { name: field.key as string, value: null } });
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

	const fieldId = field.key as string;

	return (
		<div>
			<input
				id={`${fieldId}-file-input`}
				ref={fileInputRef}
				type="file"
				className="d-none"
				onChange={handleInputChange}
			/>
			<div
				id={`${fieldId}-drop-zone`}
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
									id={`${fieldId}-preview-btn`}
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
										id={`${fieldId}-preview-btn`}
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
								id={`${fieldId}-download-btn`}
								variant={"outline-primary"}
								className="file-drop-action-btn"
								onClick={handleDownload}
								title="Download"
							>
								<i className="bi bi-download" />
							</Button>
							<Button
								id={`${fieldId}-remove-btn`}
								variant={"outline-danger"}
								className="file-drop-action-btn"
								onClick={handleRemove}
								title="Remove"
							>
								<i className="bi bi-x-lg" />
							</Button>
							{extraActions}
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
						{extraActions && (
							<div className="file-drop-actions" onClick={(e) => e.stopPropagation()}>
								{extraActions}
							</div>
						)}
					</>
				)}
			</div>
			{uploadError && <div className="text-danger mt-1 small">{uploadError}</div>}
		</div>
	);
};
