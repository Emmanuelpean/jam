import React, { useRef, useState, JSX, ReactNode, useEffect } from "react";
import { createPortal } from "react-dom";
import { Button, Form, Modal } from "react-bootstrap";
import { useAuth } from "../../../contexts/AuthContext";
import { useConfig } from "../../../contexts/ConfigContext";
import { useDataContext } from "../../../contexts/DataContext";
import { filesApi } from "../../../services/api/DataTables";
import { FileData, FileWithContentData } from "../../../services/schemas/DataTables";
import { ApiResponse } from "../../../services/api/Base";
import { canPreviewFile, fileToBase64, formatFileSize } from "../../../utils/FileUtils";
import { WidgetProps } from "./WidgetRenders";
import { Textarea } from "./TextArea";
import { ModalFormField } from "../form/FormRenders";
import { ActionButton } from "../form/ActionButton";
import JamModal from "../../JamModal/JamModal";
import "./FileUploadWidget.scss";

export interface FileUploadWidgetProps extends WidgetProps {
	extraActions?: ReactNode;
	textEditable?: boolean;
}

export const FileUploadWidget = ({
	field,
	value,
	handleChange,
	data,
	onUploadingChange,
	extraActions,
	textEditable,
}: FileUploadWidgetProps): JSX.Element => {
	const { token } = useAuth();
	const { config } = useConfig();
	const { addEntity, files, companies } = useDataContext();
	const fileInputRef = useRef<HTMLInputElement>(null);
	const tooltipRef = useRef<HTMLDivElement>(null);
	const [uploading, setUploading] = useState<boolean>(false);
	const [uploadError, setUploadError] = useState<string | null>(null);
	const [dragOver, setDragOver] = useState<boolean>(false);
	const [tooltipCoords, setTooltipCoords] = useState<{ top: number; left: number } | null>(null);

	const [savedText, setSavedText] = useState<string>("");
	const [draftText, setDraftText] = useState<string>("");
	const [filenameInput, setFilenameInput] = useState<string>("cover_letter.txt");
	const [showTextModal, setShowTextModal] = useState<boolean>(false);
	const [saving, setSaving] = useState<boolean>(false);
	const [saveError, setSaveError] = useState<string | null>(null);
	const lastValueRef = useRef<number | null | undefined>(undefined);

	const fileType = field.fileType ?? null;
	const fileMetadata: FileData | null = value ? (files.find((f) => f.id === value) ?? null) : null;
	const isTextFile = fileMetadata?.type === "text/plain";

	useEffect((): void => {
		if (!textEditable) return;
		if (value === lastValueRef.current) return;
		lastValueRef.current = value ?? null;

		if (value && isTextFile && token) {
			void filesApi.getContent(value, token).then((result: ApiResponse<FileWithContentData>): void => {
				const raw = result.data.content;
				const base64 = raw.startsWith("data:") ? (raw.split(",")[1] ?? raw) : raw;
				try {
					const decoded = decodeURIComponent(escape(atob(base64)));
					setSavedText(decoded);
				} catch {
					setSavedText(raw);
				}
			});
		} else if (!value) {
			setSavedText("");
		}
	}, [value]);

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
			const rawContent = await fileToBase64(file);
			if (typeof rawContent !== "string") throw new Error("Failed to read file as base64 string");
			const result = await addEntity("file", {
				filename: file.name,
				content: rawContent,
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

	const openTextModal = (): void => {
		setDraftText(savedText);
		if (fileMetadata?.filename) {
			setFilenameInput(fileMetadata.filename);
		} else {
			const jobTitle = (data?.title ?? "").trim();
			const companyName = (companies.find((c) => c.id === data?.company_id)?.name ?? "").trim();
			const parts = ["cover letter", jobTitle, companyName].filter(Boolean);
			const sanitized = parts.join(" ").replace(/[<>:"/\\|?*]/g, "").replace(/\s+/g, " ").trim();
			setFilenameInput(sanitized ? `${sanitized}.txt` : "cover_letter.txt");
		}
		setSaveError(null);
		setShowTextModal(true);
	};

	const handleTextSave = async (): Promise<void> => {
		if (!token) return;

		if (!draftText.trim()) {
			if (isTextFile) {
				handleChange({ target: { name: field.key as string, value: null } });
				setSavedText("");
			}
			setShowTextModal(false);
			return;
		}

		if (draftText === savedText && filenameInput === (fileMetadata?.filename ?? "cover_letter.txt")) {
			setShowTextModal(false);
			return;
		}

		const filename = filenameInput.trim() || "cover_letter.txt";
		if (config?.column_limits?.file_name && filename.length > config.column_limits.file_name) {
			setSaveError(`Filename exceeds the maximum allowed length of ${config.column_limits.file_name} characters.`);
			return;
		}

		setSaving(true);
		onUploadingChange?.(true);
		setSaveError(null);
		try {
			const base64 = btoa(unescape(encodeURIComponent(draftText)));
			const content = `data:text/plain;base64,${base64}`;
			const size = new Blob([draftText]).size;
			const result = await addEntity("file", {
				filename: filename,
				content,
				type: "text/plain",
				size,
				file_type: fileType,
			});
			setSavedText(draftText);
			lastValueRef.current = result.data.id;
			handleChange({ target: { name: field.key as string, value: result.data.id } });
			setShowTextModal(false);
		} catch (err: any) {
			setSaveError(err.message || "Failed to save text");
		} finally {
			setSaving(false);
			onUploadingChange?.(false);
		}
	};

	const hasFile: boolean = !!value && !!fileMetadata;

	const fieldId = field.key as string;

	const pencilButton = textEditable && (!hasFile || isTextFile) ? (
		<Button
			id={`${fieldId}-write-btn`}
			variant={"outline-primary"}
			className="rounded-circle p-0 d-flex align-items-center justify-content-center file-drop-action-btn cover-letter-pencil-btn"
			style={{ width: 32, height: 32 }}
			title="Edit text"
			onClick={openTextModal}
		>
			<i className="bi bi-pencil" style={{ fontSize: "0.8rem" }} />
		</Button>
	) : null;

	const allExtraActions = (
		<>
			{pencilButton}
			{extraActions}
		</>
	);

	return (
		<>
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
								{allExtraActions}
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
							{(textEditable || extraActions) && (
								<div className="file-drop-actions" onClick={(e) => e.stopPropagation()}>
									{allExtraActions}
								</div>
							)}
						</>
					)}
				</div>
				{uploadError && <div className="text-danger mt-1 small">{uploadError}</div>}
			</div>

			{textEditable && (
				<JamModal
					id="cover-letter-text-modal"
					show={showTextModal}
					onHide={() => setShowTextModal(false)}
					size="lg"
					centered
				>
					<JamModal.Header onClose={() => setShowTextModal(false)}>
						<Modal.Title>Cover Letter Text</Modal.Title>
					</JamModal.Header>
					<JamModal.Body>
						<Form.Group className="mb-2">
							<Form.Label>Filename</Form.Label>
							<Form.Control
								id="cover-letter-text-modal-filename"
								type="text"
								value={filenameInput}
								onChange={(e) => setFilenameInput(e.target.value)}
								disabled={saving}
								placeholder="cover_letter.txt"
							/>
						</Form.Group>
						<Textarea
							field={
								{
									key: "cover_letter_text",
									type: "textarea",
									rows: 16,
									placeholder: "Write or paste your cover letter here...",
									isDisabled: saving,
								} as ModalFormField
							}
							value={draftText}
							handleChange={(e) => setDraftText((e as any).target.value)}
						/>
						{saveError && <div className="text-danger mt-2 small">{saveError}</div>}
					</JamModal.Body>
					<Modal.Footer>
						<div className="d-flex flex-column w-100 gap-2">
							<div className="modal-buttons-container">
								<ActionButton
									id="cover-letter-text-modal-cancel-button"
									variant="secondary"
									defaultText="Cancel"
									onClick={() => setShowTextModal(false)}
									disabled={saving}
								/>
								<ActionButton
									id="cover-letter-text-modal-save-button"
									variant="primary"
									defaultText="Save"
									loadingText="Saving..."
									loading={saving}
									onClick={handleTextSave}
								/>
							</div>
						</div>
					</Modal.Footer>
				</JamModal>
			)}
		</>
	);
};
