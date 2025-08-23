import { useContext, useState } from "react";
import { ToastContext } from "../App";

// Define the toast variant types
type ToastVariant = "success" | "danger" | "warning" | "info";

// Define the toast object structure
interface Toast {
	id: number;
	show: boolean;
	message: string;
	variant: ToastVariant;
	title: string | null;
	delay: number;
}

// Define the return type for useToast hook
interface UseToastReturn {
	toasts: Toast[];
	showToast: (message: string, variant?: ToastVariant, title?: string | null, delay?: number) => void;
	hideToast: (id: number) => void;
	hideAllToasts: () => void;
	showSuccess: (message: string, title?: string | null, delay?: number) => void;
	showError: (message: string, title?: string | null, delay?: number) => void;
	showWarning: (message: string, title?: string | null, delay?: number) => void;
	showInfo: (message: string, title?: string | null, delay?: number) => void;
}

// Define the context type (this should match what's provided by ToastContext)
interface ToastContextType {
	toasts: Toast[];
	showToast: (message: string, variant?: ToastVariant, title?: string | null, delay?: number) => void;
	hideToast: (id: number) => void;
	hideAllToasts: () => void;
	showSuccess: (message: string, title?: string | null, delay?: number) => void;
	showError: (message: string, title?: string | null, delay?: number) => void;
	showWarning: (message: string, title?: string | null, delay?: number) => void;
	showInfo: (message: string, title?: string | null, delay?: number) => void;
}

export const useToast = (): UseToastReturn => {
	const [toasts, setToasts] = useState<Toast[]>([]);

	const showToast = (
		message: string,
		variant: ToastVariant = "danger",
		title: string | null = null,
		delay: number = 5000,
	): void => {
		const id = Date.now() + Math.random(); // Generate unique ID
		const newToast: Toast = {
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

	const hideToast = (id: number): void => {
		setToasts((prev) => prev.filter((toast) => toast.id !== id));
	};

	const hideAllToasts = (): void => {
		setToasts([]);
	};

	const showSuccess = (message: string, title: string | null = null, delay: number = 5000): void => {
		showToast(message, "success", title, delay);
	};

	const showError = (message: string, title: string | null = null, delay: number = 5000): void => {
		showToast(message, "danger", title, delay);
	};

	const showWarning = (message: string, title: string | null = null, delay: number = 5000): void => {
		showToast(message, "warning", title, delay);
	};

	const showInfo = (message: string, title: string | null = null, delay: number = 5000): void => {
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

export const useGlobalToast = (): ToastContextType => {
	const context = useContext(ToastContext);

	if (!context) {
		throw new Error("useGlobalToast must be used within a ToastContext provider");
	}

	return context;
};
