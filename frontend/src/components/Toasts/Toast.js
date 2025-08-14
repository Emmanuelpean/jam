import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import "./Toast.css";

const NotificationToast = ({ show, message, variant = "danger", delay = 5000, onClose, title = null }) => {
	const [isHiding, setIsHiding] = useState(false);
	const [progress, setProgress] = useState(100);

	useEffect(() => {
		if (!show) return;

		// Progress bar animation
		const startTime = Date.now();
		const progressInterval = setInterval(() => {
			const elapsed = Date.now() - startTime;
			const remaining = Math.max(0, ((delay - elapsed) / delay) * 100);
			setProgress(remaining);
		}, 20);

		// Auto-hide timer
		const timer = setTimeout(() => {
			handleClose();
		}, delay);

		return () => {
			clearInterval(progressInterval);
			clearTimeout(timer);
		};
	}, [show, delay]);

	const handleClose = () => {
		setIsHiding(true);
		setTimeout(() => {
			onClose();
		}, 300); // Match animation duration
	};

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

	if (!show) return null;

	return (
		<div className={`custom-toast ${variant} ${isHiding ? "hiding" : ""}`} onClick={handleClose}>
			<div className="custom-toast-header">
				<div className="custom-toast-title-wrapper">
					<i className={`bi ${getIcon()} toast-icon`}></i>
					<h6 className="custom-toast-title">{getTitle()}</h6>
				</div>
				<button className="custom-toast-close" onClick={handleClose}>
					<i className="bi bi-x"></i>
				</button>
			</div>
			<div className="custom-toast-body">{message}</div>
			<div className="custom-toast-progress" style={{ width: `${progress}%` }}></div>
		</div>
	);
};

const ToastStack = ({ toasts, onClose, position = "top-end" }) => {
	if (!toasts || toasts.length === 0) {
		return null;
	}

	return (
		<div className={`custom-toast-container ${position}`}>
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
		</div>
	);
};

NotificationToast.propTypes = {
	show: PropTypes.bool.isRequired,
	message: PropTypes.string.isRequired,
	variant: PropTypes.oneOf(["success", "danger", "warning", "info"]),
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

export { ToastStack };
