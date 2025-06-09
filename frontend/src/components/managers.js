// utils/deleteUtils.js
import { displayNameFunctions } from "../components/tables/GenericTable";
import { useModal } from "../contexts/ModalContext";
import { useAuth } from "../contexts/AuthContext";

// Hook version - super clean!
export const useDeleteItem = (endpoint) => {
	const { token } = useAuth();
	const { showConfirm, showError } = useModal();

	return async (item, onSuccess = null) => {
		const itemType = endpoint.slice(0, -1);
		const displayFunction = displayNameFunctions[itemType] || displayNameFunctions.generic;
		const itemName = displayFunction(item);
		const capitalizedType = itemType.charAt(0).toUpperCase() + itemType.slice(1);

		try {
			await showConfirm({
				title: `Delete ${capitalizedType}`,
				message: `Are you sure you want to delete "${itemName}"? This action cannot be undone.`,
				confirmText: "Delete",
				cancelText: "Cancel",
			});

			const response = await fetch(`http://localhost:8000/${endpoint}/${item.id}/`, {
				method: "DELETE",
				headers: {
					Authorization: `Bearer ${token}`,
				},
			});

			if (response.ok) {
				if (onSuccess) onSuccess(item.id);
				return true;
			} else {
				await showError({
					message: `Failed to delete ${itemType}. Please try again.`,
				});
				return false;
			}
		} catch (error) {
			if (error.message && error.message.includes("cancelled")) {
				console.log(`${capitalizedType} deletion cancelled`);
				return false;
			} else {
				console.error(`Error deleting ${itemType}:`, error);
				await showError({
					message: `Failed to delete ${itemType}. Please check your connection and try again.`,
				});
				return false;
			}
		}
	};
};
