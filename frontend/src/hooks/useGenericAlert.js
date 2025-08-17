import { useState } from "react";

const useGenericAlert = () => {
	const [alertState, setAlertState] = useState({
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
		onCancel = null,
	}) => {
		return new Promise((resolve, reject) => {
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
				onSuccess: () => {
					if (onSuccess) onSuccess();
					resolve(true);
					hideAlert();
				},
				onCancel: () => {
					if (onCancel) onCancel();
					reject(false);
					hideAlert();
				},
			});
		});
	};

	const hideAlert = () => {
		setAlertState((prev) => ({
			...prev,
			show: false,
		}));
	};

	const showSuccess = ({
		title = "Success",
		message,
		confirmText = "OK",
		size = "md",
		id = null,
		onSuccess = null,
	} = {}) => {
		return showAlert({
			title: title,
			message: message,
			type: "success",
			confirmText: confirmText,
			icon: "bi bi-check-circle-fill",
			size: size,
			id: id || "success-alert-modal",
			onSuccess: onSuccess,
		});
	};

	const showError = ({
		title = "Error",
		message,
		confirmText = "OK",
		size = "md",
		id = null,
		onSuccess = null,
	} = {}) => {
		return showAlert({
			title: title,
			message: message,
			type: "danger",
			confirmText: confirmText,
			icon: "bi bi-exclamation-triangle-fill",
			size: size,
			id: id || "error-alert-modal",
			onSuccess: onSuccess,
		});
	};

	const showWarning = ({
		title = "Warning",
		message,
		confirmText = "OK",
		size = "md",
		id = null,
		onSuccess = null,
	} = {}) => {
		return showAlert({
			title: title,
			message: message,
			type: "warning",
			confirmText: confirmText,
			icon: "bi bi-exclamation-triangle-fill",
			size: size,
			id: id || "warning-alert-modal",
			onSuccess: onSuccess,
		});
	};

	const showInfo = ({
		title = "Information",
		message,
		confirmText = "OK",
		size = "md",
		id = null,
		onSuccess = null,
	} = {}) => {
		return showAlert({
			title: title,
			message: message,
			type: "info",
			confirmText: confirmText,
			icon: "bi bi-info-circle-fill",
			size: size,
			id: id || "info-alert-modal",
			onSuccess: onSuccess,
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
	} = {}) => {
		return showAlert({
			title: title,
			message: message,
			type: "danged",
			confirmText: confirmText,
			cancelText: cancelText,
			icon: "bi bi-question-circle-fill",
			size: size,
			id: id || "confirm-alert-modal",
			onSuccess: onSuccess,
			onCancel: onCancel,
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
	} = {}) => {
		return showAlert({
			title: title,
			message: message,
			type: "danger",
			confirmText: confirmText,
			cancelText: cancelText,
			icon: "bi bi-trash-fill",
			size: size,
			id: id || "delete-alert-modal",
			onSuccess: onSuccess,
			onCancel: onCancel,
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
	} = {}) => {
		return showAlert({
			title: title,
			message: message,
			type: "warning",
			confirmText: confirmText,
			cancelText: cancelText,
			icon: "bi bi-box-arrow-right",
			size: size,
			id: id || "logout-alert-modal",
			onSuccess: onSuccess,
			onCancel: onCancel,
		});
	};

	return {
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
};

export default useGenericAlert;
