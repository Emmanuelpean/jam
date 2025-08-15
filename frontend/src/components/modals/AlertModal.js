import React from "react";
import { Button, Modal } from "react-bootstrap";

const DEFAULT_ALERT_ICONS = {
	success: "bi-check-circle-fill text-success",
	warning: "bi-exclamation-triangle-fill text-warning",
	error: "bi-x-circle-fill text-danger",
	info: "bi-info-circle-fill text-info",
	danger: "bi-exclamation-triangle-fill text-danger",
	primary: "bi-question-circle-fill text-primary",
};

const buttonVariants = {
	success: "success",
	warning: "warning",
	error: "danger",
	info: "info",
	danger: "danger",
	primary: "primary",
};

const AlertModal = ({ alertState, hideAlert }) => {
	const iconClass = alertState.icon || DEFAULT_ALERT_ICONS[alertState.type] || DEFAULT_ALERT_ICONS.info;
	const variant = buttonVariants[alertState.type] || "primary";
	const isConfirmation = !!alertState.cancelText;

	return (
		<Modal
			show={alertState.show}
			onHide={alertState.onCancel || hideAlert}
			size={alertState.size ? alertState.size : "md"}
			centered={true}
			backdrop={true}
			keyboard={true}
		>
			<Modal.Header closeButton>
				<Modal.Title>
					{iconClass && <i className={`${iconClass} me-2`} />}
					{alertState.title}
				</Modal.Title>
			</Modal.Header>

			<Modal.Body>
				<div className={isConfirmation ? "py-2" : "text-center py-3"}>
					{typeof alertState.message === "string" ? (
						<p className="mb-0">{alertState.message}</p>
					) : (
						alertState.message
					)}
				</div>
			</Modal.Body>

			<Modal.Footer className="d-flex gap-1">
				{alertState.cancelText && (
					<Button variant="secondary" onClick={alertState.onCancel || hideAlert} className="flex-fill">
						{alertState.cancelText}
					</Button>
				)}
				{alertState.confirmText && (
					<Button variant={variant} onClick={alertState.onSuccess || hideAlert} className="flex-fill">
						{alertState.confirmText}
					</Button>
				)}
			</Modal.Footer>
		</Modal>
	);
};

export default AlertModal;
