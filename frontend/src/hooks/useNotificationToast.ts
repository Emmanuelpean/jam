import { useContext, useState } from "react";
import { ToastContext } from "../App";
import { useConfig } from "../contexts/ConfigContext";
import { errorToString, handleApiError } from "../services/api/ApiError";

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
	email?: string;
	emailBody?: string;
}

// Define the return type for useToast hook
export interface UseToastReturn {
	toasts: Toast[];
	showToast: (
		message: string,
		variant?: ToastVariant,
		title?: string | null,
		email?: string,
		emailBody?: string,
		delay?: number
	) => void;
	hideToast: (id: number) => void;
	hideAllToasts: () => void;
	showToastSuccess: (
		message: string,
		title?: string | null,
		email?: string,
		emailBody?: string,
		delay?: number
	) => void;
	showToastError: (
		message: string,
		title?: string | null,
		email?: string,
		emailBody?: string,
		delay?: number
	) => void;
	showToastWarning: (
		message: string,
		title?: string | null,
		email?: string,
		emailBody?: string,
		delay?: number
	) => void;
	showToastInfo: (message: string, title?: string | null, email?: string, emailBody?: string, delay?: number) => void;
	showApiError: (error: unknown, errorTitle: string, unknownMessage: string) => void;
}

export const useToast = (): UseToastReturn => {
	const [toasts, setToasts] = useState<Toast[]>([]);
	const { config } = useConfig();

	const showToast = (
		message: string,
		variant: ToastVariant = "danger",
		title: string | null = null,
		email?: string,
		emailBody?: string,
		delay: number = 5000
	): void => {
		const id: number = Date.now() + Math.random(); // Generate unique ID
		const newToast: Toast = {
			id,
			show: true,
			message,
			variant,
			title,
			email,
			emailBody,
			delay,
		};

		setToasts((prev: Toast[]): Toast[] => [...prev, newToast]);

		// Auto-hide after delay
		setTimeout(() => {
			hideToast(id);
		}, delay);
	};

	const hideToast = (id: number): void => {
		setToasts((prev: Toast[]): Toast[] => prev.filter((toast: Toast): boolean => toast.id !== id));
	};

	const hideAllToasts = (): void => {
		setToasts([]);
	};

	const showToastSuccess = (
		message: string,
		title: string | null = null,
		email?: string,
		emailBody?: string,
		delay: number = 5000
	): void => {
		showToast(message, "success", title, email, emailBody, delay);
	};

	const showToastError = (
		message: string,
		title: string | null = null,
		email?: string,
		emailBody?: string,
		delay: number = 5000
	): void => {
		showToast(message, "danger", title, email, emailBody, delay);
	};

	const showToastWarning = (
		message: string,
		title: string | null = null,
		email?: string,
		emailBody?: string,
		delay: number = 5000
	): void => {
		showToast(message, "warning", title, email, emailBody, delay);
	};

	const showToastInfo = (
		message: string,
		title: string | null = null,
		email?: string,
		emailBody?: string,
		delay: number = 5000
	): void => {
		showToast(message, "info", title, email, emailBody, delay);
	};

	const showApiError = (error: unknown, errorTitle: string, unknownMessage: string) => {
		const { message, status } = handleApiError(error);

		if (status && status < 500) {
			showToastError(message, errorTitle);
		} else {
			showToastError(unknownMessage, errorTitle, config.support_email, errorToString(error));
		}
	};

	return {
		toasts,
		showToast,
		hideToast,
		hideAllToasts,
		showToastSuccess,
		showToastError,
		showToastWarning,
		showToastInfo,
		showApiError,
	};
};

export const useGlobalToast = (): UseToastReturn => {
	const context = useContext(ToastContext);

	if (!context) {
		throw new Error("useGlobalToast must be used within a ToastContext provider");
	}

	return context;
};
