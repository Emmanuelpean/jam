import { useContext, useState } from "react";
import { ToastContext } from "../App";

export const useToast = () => {
	const [toasts, setToasts] = useState([]);

	const showToast = (message, variant = "danger", title = null, delay = 5000) => {
		const id = Date.now() + Math.random(); // Generate unique ID
		const newToast = {
			id,
			show: true,
			message,
			variant,
			title,
			delay,
		};

		setToasts((prev) => [...prev, newToast]);

		// Auto-hide after delay
		setTimeout(() => {
			hideToast(id);
		}, delay);
	};

	const hideToast = (id) => {
		setToasts((prev) => prev.filter((toast) => toast.id !== id));
	};

	const hideAllToasts = () => {
		setToasts([]);
	};

	const showSuccess = (message, title = null, delay = 5000) => {
		showToast(message, "success", title, delay);
	};

	const showError = (message, title = null, delay = 5000) => {
		showToast(message, "danger", title, delay);
	};

	const showWarning = (message, title = null, delay = 5000) => {
		showToast(message, "warning", title, delay);
	};

	const showInfo = (message, title = null, delay = 5000) => {
		showToast(message, "info", title, delay);
	};

	return {
		toasts,
		showToast,
		hideToast,
		hideAllToasts,
		showSuccess,
		showError,
		showWarning,
		showInfo,
	};
};

export const useGlobalToast = () => {
	const context = useContext(ToastContext);

	if (!context) {
		throw new Error("useGlobalToast must be used within a ToastContext provider");
	}

	return context;
};
