import React from "react";
import GenericModal from "../GenericModal";

const AlertModal = ({ alertState, hideAlert }) => {
	return (
		<GenericModal
			show={alertState.show}
			onHide={hideAlert}
			mode={alertState.cancelText ? "confirmation" : "alert"}
			title={alertState.title}
			alertMessage={alertState.message}
			confirmationMessage={alertState.message}
			alertType={alertState.type}
			confirmText={alertState.confirmText}
			cancelText={alertState.cancelText}
			alertIcon={alertState.icon}
			size={alertState.size}
			onSuccess={alertState.onSuccess}
			onConfirm={alertState.onSuccess}
		/>
	);
};

export default AlertModal;
