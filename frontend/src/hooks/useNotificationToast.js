import { useState } from "react";

const useToast = () => {
	const [toast, setToast] = useState({
		show: false,
		message: "",
		variant: "danger",
		title: null,
	});

	const showToast = (message, variant = "danger", title = null) => {
		setToast({
			show: true,
			message,
			variant,
			title,
		});
	};

	const hideToast = () => {
		setToast((prev) => ({
			...prev,
			show: false,
		}));
	};

	const showSuccess = (message, title = null) => {
		showToast(message, "success", title);
	};

	const showError = (message, title = null) => {
		showToast(message, "danger", title);
	};

	const showWarning = (message, title = null) => {
		showToast(message, "warning", title);
	};

	const showInfo = (message, title = null) => {
		showToast(message, "info", title);
	};

	return {
		toast,
		showToast,
		hideToast,
		showSuccess,
		showError,
		showWarning,
		showInfo,
	};
};

export default useToast;
