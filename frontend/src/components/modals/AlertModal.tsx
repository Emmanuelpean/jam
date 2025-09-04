import React from "react";
import { Button, Modal } from "react-bootstrap";

type AlertType = "success" | "warning" | "error" | "info" | "danger" | "primary";

export interface AlertState {
	show: boolean;
	type?: AlertType;
	title?: string;
	message?: string | React.ReactNode;
	icon?: string | null;
	size?: "sm" | "md" | "lg" | "xl";
	id?: string | null;
	cancelText?: string | null;
	confirmText?: string;
	onCancel?: (() => void) | null;
	onSuccess?: (() => void) | null;
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

const buttonVariants: Record<AlertType, string> = {
	success: "success",
	warning: "warning",
	error: "danger",
	info: "info",
	danger: "danger",
	primary: "primary",
};

const AlertModal: React.FC<AlertModalProps> = ({ alertState, hideAlert }) => {
	const iconClass = alertState.icon || DEFAULT_ALERT_ICONS[alertState.type || "info"] || DEFAULT_ALERT_ICONS.info;
	const variant = buttonVariants[alertState.type || "primary"] || "primary";
	const isConfirmation = !!alertState.cancelText;

	// Generate a fallback ID if none is provided
	const modalId = alertState.id || `alert-modal-${alertState.type || "default"}`;

	// Handle size prop - "md" is the default for Modal, so we pass undefined for "md"
	const modalSize = alertState.size && alertState.size !== "md" ? (alertState.size as "sm" | "lg" | "xl") : undefined;

	return (
		<Modal
			id={modalId}
			show={alertState.show}
			onHide={alertState.onCancel || hideAlert}
			size={modalSize}
			centered={true}
			backdrop={true}
			keyboard={true}
		>
			<Modal.Header closeButton>
				<Modal.Title id={`${modalId}-title`}>
					{iconClass && <i className={`${iconClass} me-2`} />}
					{alertState.title}
				</Modal.Title>
			</Modal.Header>

			<Modal.Body id={`${modalId}-body`}>
				<div className={isConfirmation ? "py-2" : "text-center py-3"}>
					{typeof alertState.message === "string" ? (
						<p className="mb-0">{alertState.message}</p>
					) : (
						alertState.message
					)}
				</div>
			</Modal.Body>

			<Modal.Footer className="d-flex gap-1" id={`${modalId}-footer`}>
				{alertState.cancelText && (
					<Button
						id={`${modalId}-cancel-button`}
						variant="secondary"
						onClick={alertState.onCancel || hideAlert}
						className="flex-fill"
					>
						{alertState.cancelText}
					</Button>
				)}
				{alertState.confirmText && (
					<Button
						id={`${modalId}-confirm-button`}
						variant={variant}
						onClick={alertState.onSuccess || hideAlert}
						className="flex-fill"
					>
						{alertState.confirmText}
					</Button>
				)}
			</Modal.Footer>
		</Modal>
	);
};

export default AlertModal;
