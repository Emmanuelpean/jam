import React from "react";
import { Toast, ToastContainer } from "react-bootstrap";
import PropTypes from "prop-types";

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
		<ToastContainer position={position} className="p-3">
			<Toast show={show} onClose={onClose} autohide delay={delay} bg={variant}>
				<Toast.Header>
					<i className={`bi ${getIcon()} me-2`}></i>
					<strong className="me-auto">{getTitle()}</strong>
				</Toast.Header>
				<Toast.Body className="text-white">{message}</Toast.Body>
			</Toast>
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

export default NotificationToast;
