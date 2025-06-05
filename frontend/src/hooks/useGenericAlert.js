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

	// Default alert presets with Bootstrap icons
	const showSuccess = ({ title = "Success", message, confirmText = "OK", size = "md", onSuccess = null } = {}) => {
		return showAlert({
			title,
			message,
			type: "success",
			confirmText,
			icon: "bi bi-check-circle-fill",
			size,
			onSuccess,
		});
	};

	const showError = ({ title = "Error", message, confirmText = "OK", size = "md", onSuccess = null } = {}) => {
		return showAlert({
			title,
			message,
			type: "danger",
			confirmText,
			icon: "bi bi-exclamation-triangle-fill",
			size,
			onSuccess,
		});
	};

	const showWarning = ({ title = "Warning", message, confirmText = "OK", size = "md", onSuccess = null } = {}) => {
		return showAlert({
			title,
			message,
			type: "warning",
			confirmText,
			icon: "bi bi-exclamation-triangle-fill",
			size,
			onSuccess,
		});
	};

	const showInfo = ({ title = "Information", message, confirmText = "OK", size = "md", onSuccess = null } = {}) => {
		return showAlert({
			title,
			message,
			type: "info",
			confirmText,
			icon: "bi bi-info-circle-fill",
			size,
			onSuccess,
		});
	};

	const showConfirm = ({
		title = "Confirm Action",
		message,
		confirmText = "Yes",
		cancelText = "No",
		size = "md",
		onSuccess = null,
		onCancel = null,
	} = {}) => {
		return showAlert({
			title,
			message,
			type: "primary",
			confirmText,
			cancelText,
			icon: "bi bi-question-circle-fill",
			size,
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
		onSuccess = null,
		onCancel = null,
	} = {}) => {
		return showAlert({
			title,
			message,
			type: "danger",
			confirmText,
			cancelText,
			icon: "bi bi-trash-fill",
			size,
			onSuccess,
			onCancel,
		});
	};

	const showSave = ({
		title = "Save Changes",
		message = "Do you want to save your changes?",
		confirmText = "Save",
		cancelText = "Cancel",
		size = "md",
		onSuccess = null,
		onCancel = null,
	} = {}) => {
		return showAlert({
			title,
			message,
			type: "primary",
			confirmText,
			cancelText,
			icon: "bi bi-floppy-fill",
			size,
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
		onSuccess = null,
		onCancel = null,
	} = {}) => {
		return showAlert({
			title,
			message,
			type: "warning",
			confirmText,
			cancelText,
			icon: "bi bi-box-arrow-right",
			size,
			onSuccess,
			onCancel,
		});
	};

	const showLoading = ({ title = "Loading", message = "Please wait...", size = "md" } = {}) => {
		return showAlert({
			title,
			message,
			type: "info",
			confirmText: null, // No button for loading
			icon: "bi bi-hourglass-split",
			size,
		});
	};

	const showDownload = ({
		title = "Download",
		message,
		confirmText = "Download",
		cancelText = "Cancel",
		size = "md",
		onSuccess = null,
		onCancel = null,
	} = {}) => {
		return showAlert({
			title,
			message,
			type: "info",
			confirmText,
			cancelText,
			icon: "bi bi-download",
			size,
			onSuccess,
			onCancel,
		});
	};

	const showUpload = ({
		title = "Upload File",
		message,
		confirmText = "Upload",
		cancelText = "Cancel",
		size = "md",
		onSuccess = null,
		onCancel = null,
	} = {}) => {
		return showAlert({
			title,
			message,
			type: "primary",
			confirmText,
			cancelText,
			icon: "bi bi-upload",
			size,
			onSuccess,
			onCancel,
		});
	};

	const showNetwork = ({
		title = "Network Error",
		message = "Unable to connect to the server. Please check your internet connection and try again.",
		confirmText = "Retry",
		cancelText = "Cancel",
		size = "md",
		onSuccess = null,
		onCancel = null,
	} = {}) => {
		return showAlert({
			title,
			message,
			type: "danger",
			confirmText,
			cancelText,
			icon: "bi bi-wifi-off",
			size,
			onSuccess,
			onCancel,
		});
	};

	return {
		alertState,
		showAlert,
		hideAlert,
		// Preset alerts
		showSuccess,
		showError,
		showWarning,
		showInfo,
		showConfirm,
		showDelete,
		showSave,
		showLogout,
		showLoading,
		showDownload,
		showUpload,
		showNetwork,
	};
};

export default useGenericAlert;
