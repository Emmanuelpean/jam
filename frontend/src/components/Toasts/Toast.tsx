import React, { useEffect, useState, JSX } from "react";
import "./Toast.scss";

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
	email?: string;
	emailBody?: string;
}

// Props for NotificationToast component
interface NotificationToastProps {
	show: boolean;
	message: string;
	variant: ToastVariant;
	delay: number;
	onClose: () => void;
	title: string | null;
	emailAddress?: string;
	emailBody?: string;
}

// Props for ToastStack component
interface ToastStackProps {
	toasts: Toast[];
	onClose: (id: number) => void;
	position?: ToastPosition;
}

const NotificationToast: React.FC<NotificationToastProps> = ({
	show,
	message,
	variant,
	delay,
	onClose,
	title,
	emailAddress,
	emailBody,
}: NotificationToastProps): JSX.Element | null => {
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

	const handleContextMenu = (_: any): void => {
		if (!emailAddress) return;
		window.location.href = emailBody
			? `mailto:${emailAddress}?body=${encodeURIComponent(emailBody)}`
			: `mailto:${emailAddress}`;
		handleClose();
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
		<div
			className={`custom-toast ${variant} ${isHiding ? "hiding" : ""}`}
			onClick={handleClose}
			onContextMenu={handleContextMenu}
		>
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
				{emailAddress && (
					<div className="text-muted" style={{ fontSize: "0.85em", marginTop: "0.5rem" }}>
						Right-click to send email
					</div>
				)}
			</div>
			<div className="custom-toast-progress" style={{ height: `${progress}%` }}></div>
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
					emailAddress={toast.email}
					emailBody={toast.emailBody}
					onClose={() => onClose(toast.id)}
				/>
			))}
		</div>
	);
};

export { ToastStack };
