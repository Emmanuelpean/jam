import React, { useState, useEffect } from "react";
import "./Toast.css";

// Define the toast variant types
type ToastVariant = "success" | "danger" | "warning" | "info";

// Define the position types for ToastStack
type ToastPosition =
	| "top-start"
	| "top-center"
	| "top-end"
	| "middle-start"
	| "middle-center"
	| "middle-end"
	| "bottom-start"
	| "bottom-center"
	| "bottom-end";

// Define the toast object structure - match useNotificationToast.ts
interface Toast {
	id: number;
	show: boolean;
	message: string;
	variant: ToastVariant;
	title: string | null;
	delay: number;
}

// Props for NotificationToast component
interface NotificationToastProps {
	show: boolean;
	message: string;
	variant: ToastVariant;
	delay: number;
	onClose: () => void;
	title: string | null;
}

// Props for ToastStack component
interface ToastStackProps {
	toasts: Toast[];
	onClose: (id: number) => void;
	position?: ToastPosition;
}

const NotificationToast: React.FC<NotificationToastProps> = ({ show, message, variant, delay, onClose, title }) => {
	const [isHiding, setIsHiding] = useState<boolean>(false);
	const [progress, setProgress] = useState<number>(100);

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

	const handleClose = (): void => {
		setIsHiding(true);
		setTimeout(() => {
			onClose();
		}, 300); // Match animation duration
	};

	const getIcon = (): string => {
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

	const getTitle = (): string => {
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
			<div className="custom-toast-body" id="toast">
				{message}
			</div>
			<div className="custom-toast-progress" style={{ width: `${progress}%` }}></div>
		</div>
	);
};

const ToastStack: React.FC<ToastStackProps> = ({ toasts, onClose, position = "top-end" }) => {
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

export { ToastStack };
