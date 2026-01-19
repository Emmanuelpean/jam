import React, { JSX, useState } from "react";
import { Modal } from "react-bootstrap";
import { ActionButton, ButtonVariant } from "../rendering/form/ActionButton";

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
	loadingText?: string;
	onCancel?: (() => void) | null;
	onSuccess?: (() => void | Promise<void>) | null;
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
	const modalSize = alertState.size && alertState.size !== "md" ? (alertState.size as "sm" | "lg" | "xl") : undefined;
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

	return (
		<Modal show={alertState.show} onHide={hideAlert} centered size={modalSize} id={modalId}>
			<Modal.Header closeButton>
				{iconClass && <i className={`bi ${iconClass} me-2`} />}
				<Modal.Title>{alertState.title}</Modal.Title>
			</Modal.Header>
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
							variant="secondary"
							onClick={() => {
								alertState.onCancel?.();
								hideAlert();
							}}
							disabled={loading}
							defaultText={alertState.cancelText}
						/>
					)}
					{alertState.confirmText && (
						<ActionButton
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
