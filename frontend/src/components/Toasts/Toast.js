import React from "react";
import { Toast, ToastContainer } from "react-bootstrap";
import PropTypes from "prop-types";
import "./Toast.css";

const NotificationToast = ({
	show,
	message,
	variant = "danger",
	position = "top-end",
	delay = 5000,
	onClose,
	title = null,
}) => {
	const getIcon = () => {
		switch (variant) {
			case "success":
				return "bi-check-circle-fill";
			case "warning":
				return "bi-exclamation-triangle-fill";
			case "info":
				return "bi-info-circle-fill";
			case "danger":
			default:
				return "bi-exclamation-triangle-fill";
		}
	};

	const getTitle = () => {
		if (title) return title;

		switch (variant) {
			case "success":
				return "Success";
			case "warning":
				return "Warning";
			case "info":
				return "Information";
			case "danger":
			default:
				return "Error";
		}
	};

	return (
		<Toast show={show} onClose={onClose} autohide delay={delay} bg={variant}>
			<Toast.Header>
				<i className={`bi ${getIcon()} me-2`}></i>
				<strong className="me-auto">{getTitle()}</strong>
			</Toast.Header>
			<Toast.Body className="text-white">{message}</Toast.Body>
		</Toast>
	);
};

// New component for stacking multiple toasts
const ToastStack = ({ toasts, onClose, position = "top-end" }) => {
	if (!toasts || toasts.length === 0) {
		return null;
	}

	return (
		<ToastContainer position={position} className="p-3">
			{toasts.map((toast) => (
				<NotificationToast
					key={toast.id}
					show={toast.show}
					message={toast.message}
					variant={toast.variant}
					title={toast.title}
					delay={toast.delay}
					onClose={() => onClose(toast.id)}
				/>
			))}
		</ToastContainer>
	);
};

NotificationToast.propTypes = {
	show: PropTypes.bool.isRequired,
	message: PropTypes.string.isRequired,
	variant: PropTypes.oneOf(["success", "danger", "warning", "info"]),
	position: PropTypes.oneOf([
		"top-start",
		"top-center",
		"top-end",
		"middle-start",
		"middle-center",
		"middle-end",
		"bottom-start",
		"bottom-center",
		"bottom-end",
	]),
	delay: PropTypes.number,
	onClose: PropTypes.func.isRequired,
	title: PropTypes.string,
};

ToastStack.propTypes = {
	toasts: PropTypes.arrayOf(
		PropTypes.shape({
			id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
			show: PropTypes.bool.isRequired,
			message: PropTypes.string.isRequired,
			variant: PropTypes.oneOf(["success", "danger", "warning", "info"]),
			title: PropTypes.string,
			delay: PropTypes.number,
		}),
	).isRequired,
	onClose: PropTypes.func.isRequired,
	position: PropTypes.oneOf([
		"top-start",
		"top-center",
		"top-end",
		"middle-start",
		"middle-center",
		"middle-end",
		"bottom-start",
		"bottom-center",
		"bottom-end",
	]),
};

export default NotificationToast;
export { ToastStack };
