import React, { JSX, useState } from "react";
import { Modal } from "react-bootstrap";
import { ActionButton, ButtonVariant } from "../rendering/form/ActionButton";
import { ModalHeader } from "../ModalHeader/ModalHeader";

export type AlertType = "success" | "warning" | "error" | "info" | "danger" | "primary";
export type BootstrapModalSize = "sm" | "lg" | "xl" | undefined;
export type ModalSize = "sm" | "md" | "lg" | "xl";

export const getModalSize = (size?: ModalSize): BootstrapModalSize => {
	return size && size !== "md" ? (size as "sm" | "lg" | "xl") : undefined;
};

export interface AlertState {
	show: boolean;
	type?: AlertType;
	title?: string;
	message?: string;
	icon?: string | null;
	size?: ModalSize;
	id?: string | null;
	cancelText?: string | null;
	confirmText?: string;
	loadingText?: string;
	onSuccess?: (() => void | Promise<void>) | null;
	onCancel?: (() => void | Promise<void>) | null;
}

interface AlertModalProps {
	alertState: AlertState;
	hideAlert: () => void;
}

const DEFAULT_ALERT_ICONS: Record<AlertType, string> = {
	success: "bi-check-circle-fill text-success",
	warning: "bi-exclamation-triangle-fill text-warning",
	error: "bi-x-circle-fill text-danger",
	info: "bi-info-circle-fill text-info",
	danger: "bi-exclamation-triangle-fill text-danger",
	primary: "bi-question-circle-fill text-primary",
};

const buttonVariants: Record<AlertType, ButtonVariant> = {
	success: "success",
	warning: "warning",
	error: "danger",
	info: "info",
	danger: "danger",
	primary: "primary",
};

const AlertModal: React.FC<AlertModalProps> = ({ alertState, hideAlert }: AlertModalProps): JSX.Element => {
	const iconClass: string =
		alertState.icon || DEFAULT_ALERT_ICONS[alertState.type || "info"] || DEFAULT_ALERT_ICONS.info;
	const variant: ButtonVariant = buttonVariants[alertState.type || "primary"] || "primary";
	const modalId: string = alertState.id || `alert-modal-${alertState.type || "default"}`;
	const [loading, setLoading] = useState<boolean>(false);

	const handleConfirm = async (): Promise<void> => {
		if (alertState.onSuccess) {
			setLoading(true);
			try {
				await alertState.onSuccess();
				hideAlert();
			} catch (error) {
			} finally {
				setLoading(false);
			}
		} else {
			hideAlert();
		}
	};

	const handleCancel = async (): Promise<void> => {
		alertState.onCancel?.();
		hideAlert();
	};

	return (
		<Modal show={alertState.show} onHide={hideAlert} centered size={getModalSize(alertState.size)} id={modalId}>
			<ModalHeader onClose={hideAlert}>
				{iconClass && <i className={`bi ${iconClass} me-2`} />}
				<Modal.Title>{alertState.title}</Modal.Title>
			</ModalHeader>
			<Modal.Body>
				{typeof alertState.message === "string" ? (
					<p className="mb-0">{alertState.message}</p>
				) : (
					alertState.message
				)}
			</Modal.Body>
			<Modal.Footer>
				<div className="modal-buttons-container">
					{alertState.cancelText && (
						<ActionButton
							id={`${modalId}-cancel-button`}
							variant="secondary"
							onClick={handleCancel}
							disabled={loading}
							defaultText={alertState.cancelText}
						/>
					)}
					{alertState.confirmText && (
						<ActionButton
							id={`${modalId}-confirm-button`}
							variant={variant}
							onClick={handleConfirm}
							loading={loading}
							loadingText={alertState.loadingText || "Processing..."}
							disabled={loading}
							defaultText={alertState.confirmText}
						/>
					)}
				</div>
			</Modal.Footer>
		</Modal>
	);
};

export default AlertModal;
