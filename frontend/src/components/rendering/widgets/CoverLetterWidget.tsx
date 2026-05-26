import React, { JSX, useEffect, useRef, useState } from "react";
import { Button, Modal } from "react-bootstrap";
import { useAuth } from "../../../contexts/AuthContext";
import { useDataContext } from "../../../contexts/DataContext";
import { filesApi } from "../../../services/api/DataTables";
import { FileWithContentData } from "../../../services/schemas/DataTables";
import { ApiResponse } from "../../../services/api/Base";
import { FileUploadWidget, FileUploadWidgetProps } from "./FileUploadWidget";
import { WidgetProps } from "./WidgetRenders";
import { Textarea } from "./TextArea";
import { ModalFormField } from "../form/FormRenders";
import { ActionButton } from "../form/ActionButton";
import "./CoverLetterWidget.scss";
import JamModal from "../../JamModal/JamModal";

export const CoverLetterWidget = (props: WidgetProps): JSX.Element => {
	const { field, value, handleChange, onUploadingChange } = props;
	const { token } = useAuth();
	const { files, addEntity } = useDataContext();

	const fileMetadata = value ? (files.find((f) => f.id === value) ?? null) : null;
	const isTextFile = fileMetadata?.type === "text/plain";

	const [savedText, setSavedText] = useState<string>("");
	const [draftText, setDraftText] = useState<string>("");
	const [showModal, setShowModal] = useState<boolean>(false);
	const [uploading, setUploading] = useState<boolean>(false);
	const [uploadError, setUploadError] = useState<string | null>(null);
	const lastValueRef = useRef<number | null>(value ?? null);

	useEffect((): void => {
		if (value === lastValueRef.current) return;
		lastValueRef.current = value ?? null;

		if (value && isTextFile && token) {
			void filesApi.getContent(value, token).then((result: ApiResponse<FileWithContentData>): void => {
				const raw = result.data.content;
				try {
					const decoded = decodeURIComponent(escape(atob(raw)));
					setSavedText(decoded);
				} catch {
					setSavedText(raw);
				}
			});
		} else if (!value) {
			setSavedText("");
		}
	}, [value]);

	const openModal = (): void => {
		setDraftText(savedText);
		setUploadError(null);
		setShowModal(true);
	};

	const handleSave = async (): Promise<void> => {
		if (!token) return;

		if (!draftText.trim()) {
			if (isTextFile) {
				handleChange({ target: { name: field.key as string, value: null } });
				setSavedText("");
			}
			setShowModal(false);
			return;
		}

		if (draftText === savedText) {
			setShowModal(false);
			return;
		}

		setUploading(true);
		onUploadingChange?.(true);
		setUploadError(null);
		try {
			const base64 = btoa(unescape(encodeURIComponent(draftText)));
			const content = `data:text/plain;base64,${base64}`;
			const size = new Blob([draftText]).size;
			const result = await addEntity("file", {
				filename: "cover_letter.txt",
				content,
				type: "text/plain",
				size,
				file_type: "cover_letter",
			});
			setSavedText(draftText);
			lastValueRef.current = result.data.id;
			handleChange({ target: { name: field.key as string, value: result.data.id } });
			setShowModal(false);
		} catch (err: any) {
			setUploadError(err.message || "Failed to save text");
		} finally {
			setUploading(false);
			onUploadingChange?.(false);
		}
	};

	const pencilButton = (
		<Button
			id="cover-letter-write-btn"
			variant={"outline-primary"}
			className="rounded-circle p-0 d-flex align-items-center justify-content-center file-drop-action-btn cover-letter-pencil-btn"
			style={{ width: 32, height: 32 }}
			title={isTextFile ? "Edit cover letter text" : "Write cover letter text"}
			onClick={openModal}
		>
			<i className="bi bi-pencil" style={{ fontSize: "0.8rem" }} />
		</Button>
	);

	const fileUploadProps: FileUploadWidgetProps = { ...props, extraActions: pencilButton };

	return (
		<>
			<FileUploadWidget {...fileUploadProps} />

			<JamModal id="cover-letter-text-modal" show={showModal} onHide={() => setShowModal(false)} size="lg" centered>
				<JamModal.Header onClose={() => setShowModal(false)}>
					<Modal.Title>Cover Letter Text</Modal.Title>
				</JamModal.Header>
				<JamModal.Body>
					<Textarea
						field={
							{
								key: "cover_letter_text",
								type: "textarea",
								rows: 16,
								placeholder: "Write or paste your cover letter here...",
								isDisabled: uploading,
							} as ModalFormField
						}
						value={draftText}
						handleChange={(e) => setDraftText((e as any).target.value)}
					/>
					{uploadError && <div className="text-danger mt-2 small">{uploadError}</div>}
				</JamModal.Body>
				<Modal.Footer>
					<div className="d-flex flex-column w-100 gap-2">
						<div className="modal-buttons-container">
							<ActionButton
								id="cover-letter-text-modal-cancel-button"
								variant="secondary"
								defaultText="Cancel"
								onClick={() => setShowModal(false)}
								disabled={uploading}
							/>
							<ActionButton
								id="cover-letter-text-modal-save-button"
								variant="primary"
								defaultText="Save"
								loadingText="Saving..."
								loading={uploading}
								onClick={handleSave}
							/>
						</div>
					</div>
				</Modal.Footer>
			</JamModal>
		</>
	);
};
