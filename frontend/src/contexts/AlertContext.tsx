import { JSX, ReactNode, useState } from "react";
import AlertModal, { AlertState } from "../components/AlertModal/AlertModal";
import { AlertConfig, AlertContext, AlertContextType } from "./AlertContext.context";

export { useAlert } from "./AlertContext.context";
export type { AlertContextType, AlertConfig } from "./AlertContext.context";

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
		onCancel: null,
	});

	const hideAlert = (): void => {
		setAlertState((prev: AlertState): AlertState => ({ ...prev, show: false }));
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
				onCancel: (): void => {
					resolve(false);
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
	}: Partial<AlertConfig> = {}): Promise<boolean> => {
		return showAlert({
			title,
			message,
			type: "danger",
			confirmText,
			cancelText,
			icon: "bi bi-box-arrow-right",
			size,
			id: id || "logout-alert-modal",
			onSuccess,
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
