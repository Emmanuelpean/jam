import { createContext, JSX, ReactNode, useContext, useState } from "react";
import AlertModal, { AlertState } from "../components/AlertModal/AlertModal";

interface AlertConfig {
	title?: string;
	message: string;
	type?: "info" | "success" | "danger" | "warning" | "primary";
	confirmText?: string;
	cancelText?: string | null;
	icon?: string | null;
	size?: "sm" | "md" | "lg" | "xl";
	id?: string | null;
	onSuccess?: (() => void | Promise<void>) | null;
	onCancel?: (() => void) | null;
}

interface AlertContextType {
	alertState: AlertState;
	showAlert: (config: AlertConfig) => Promise<boolean>;
	hideAlert: () => void;
	showSuccess: (config?: Partial<AlertConfig>) => Promise<boolean>;
	showError: (config?: Partial<AlertConfig>) => Promise<boolean>;
	showWarning: (config?: Partial<AlertConfig>) => Promise<boolean>;
	showInfo: (config?: Partial<AlertConfig>) => Promise<boolean>;
	showConfirm: (config?: Partial<AlertConfig>) => Promise<boolean>;
	showDelete: (config?: Partial<AlertConfig>) => Promise<boolean>;
	showLogout: (config?: Partial<AlertConfig>) => Promise<boolean>;
}

const AlertContext = createContext<AlertContextType | null>(null);

export const AlertProvider = ({ children }: { children: ReactNode }): JSX.Element => {
	const [alertState, setAlertState] = useState<AlertState>({
		show: false,
		title: "Alert",
		message: "",
		type: "info",
		confirmText: "OK",
		cancelText: null,
		icon: null,
		size: "md",
		id: null,
		onSuccess: null,
	});

	const hideAlert = (): void => {
		setAlertState((prev: AlertState) => ({ ...prev, show: false }));
	};

	const showAlert = ({
		title = "Alert",
		message,
		type = "info",
		confirmText = "OK",
		cancelText = null,
		icon = null,
		size = "md",
		id = null,
		onSuccess = null,
	}: AlertConfig): Promise<boolean> => {
		return new Promise((resolve): void => {
			setAlertState({
				show: true,
				title,
				message,
				type,
				confirmText,
				cancelText,
				icon,
				size,
				id,
				onSuccess: onSuccess
					? async (): Promise<void> => {
							try {
								await onSuccess();
								resolve(true);
							} catch (error) {
								throw error;
							}
						}
					: (): void => {
							resolve(true);
						},
			});
		});
	};

	const showSuccess = ({
		title = "Success",
		message,
		confirmText = "OK",
		size = "md",
		id = null,
		onSuccess = null,
	}: Partial<AlertConfig> = {}): Promise<boolean> => {
		return showAlert({
			title,
			message: message!,
			type: "success",
			confirmText,
			icon: "bi bi-check-circle-fill",
			size,
			id: id || "success-alert-modal",
			onSuccess,
		});
	};

	const showError = ({
		title = "Error",
		message,
		confirmText = "OK",
		size = "md",
		id = null,
		onSuccess = null,
	}: Partial<AlertConfig> = {}): Promise<boolean> => {
		return showAlert({
			title,
			message: message!,
			type: "danger",
			confirmText,
			icon: "bi bi-exclamation-triangle-fill",
			size,
			id: id || "error-alert-modal",
			onSuccess,
		});
	};

	const showWarning = ({
		title = "Warning",
		message,
		confirmText = "OK",
		size = "md",
		id = null,
		onSuccess = null,
	}: Partial<AlertConfig> = {}): Promise<boolean> => {
		return showAlert({
			title,
			message: message!,
			type: "warning",
			confirmText,
			icon: "bi bi-exclamation-triangle-fill",
			size,
			id: id || "warning-alert-modal",
			onSuccess,
		});
	};

	const showInfo = ({
		title = "Information",
		message,
		confirmText = "OK",
		size = "md",
		id = null,
		onSuccess = null,
	}: Partial<AlertConfig> = {}): Promise<boolean> => {
		return showAlert({
			title,
			message: message!,
			type: "info",
			confirmText,
			icon: "bi bi-info-circle-fill",
			size,
			id: id || "info-alert-modal",
			onSuccess,
		});
	};

	const showConfirm = ({
		title = "Confirm Action",
		message,
		confirmText = "Yes",
		cancelText = "No",
		size = "md",
		id = null,
		onSuccess = null,
		onCancel = null,
	}: Partial<AlertConfig> = {}): Promise<boolean> => {
		return showAlert({
			title,
			message: message!,
			type: "primary",
			confirmText,
			cancelText,
			icon: "bi bi-question-circle-fill",
			size,
			id: id || "confirm-alert-modal",
			onSuccess,
			onCancel,
		});
	};

	const showDelete = ({
		title = "Delete Item",
		message = "Are you sure you want to delete this item? This action cannot be undone.",
		confirmText = "Delete",
		cancelText = "Cancel",
		size = "md",
		id = null,
		onSuccess = null,
		onCancel = null,
	}: Partial<AlertConfig> = {}): Promise<boolean> => {
		return showAlert({
			title,
			message,
			type: "danger",
			confirmText,
			cancelText,
			icon: "bi bi-trash-fill",
			size,
			id: id || "delete-alert-modal",
			onSuccess,
			onCancel,
		});
	};

	const showLogout = ({
		title = "Logout",
		message = "Are you sure you want to logout?",
		confirmText = "Logout",
		cancelText = "Cancel",
		size = "md",
		id = null,
		onSuccess = null,
		onCancel = null,
	}: Partial<AlertConfig> = {}): Promise<boolean> => {
		return showAlert({
			title,
			message,
			type: "warning",
			confirmText,
			cancelText,
			icon: "bi bi-box-arrow-right",
			size,
			id: id || "logout-alert-modal",
			onSuccess,
			onCancel,
		});
	};

	const value: AlertContextType = {
		alertState,
		showAlert,
		hideAlert,
		showSuccess,
		showError,
		showWarning,
		showInfo,
		showConfirm,
		showDelete,
		showLogout,
	};

	return (
		<AlertContext.Provider value={value}>
			{children}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</AlertContext.Provider>
	);
};

export const useAlert = (): AlertContextType => {
	const context: AlertContextType | null = useContext(AlertContext);
	if (!context) {
		throw new Error("useAlert must be used within AlertProvider");
	}
	return context;
};
