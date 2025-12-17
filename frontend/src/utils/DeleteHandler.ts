import { EntityType, useDataContext } from "../contexts/DataContext";
import { useGlobalToast } from "../hooks/useNotificationToast";
import { useAlert } from "../contexts/AlertContext";

const getItemName = (item: any, nameKey: string | null, itemType?: string): string => {
	if (nameKey && nameKey !== "date") {
		return `"${item[nameKey]}"`;
	} else if (itemType) {
		return `this ${itemType.toLowerCase()}`;
	} else {
		return `this item`;
	}
};

export const useDeleteHandler = (entityType: EntityType, nameKey: string | null, itemType = "item") => {
	const { deleteEntity } = useDataContext();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const { showDelete } = useAlert();

	return async (item: any): Promise<boolean> => {
		const itemName = getItemName(item, nameKey, itemType);

		try {
			const confirmed = await showDelete({
				title: `Delete ${itemType}`,
				message: `Are you sure you want to delete ${itemName}? This action cannot be undone.`,
				confirmText: "Delete",
				cancelText: "Cancel",
			});

			if (!confirmed) {
				return false;
			}

			await deleteEntity(entityType, item.id);
			showToastSuccess(`${itemType} deleted successfully.`);
			return true;
		} catch (error) {
			showToastError(`Failed to delete ${itemName}. Please check your connection and try again.`);
			return false;
		}
	};
};

export const useActiveHandler = (entityType: EntityType, nameKey: string | null, itemType = "item") => {
	const { updateEntity } = useDataContext();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const { showDelete } = useAlert();

	return async (item: any): Promise<boolean> => {
		const itemName = getItemName(item, nameKey, itemType);

		try {
			const confirmed = await showDelete({
				title: `Delete ${itemType}`,
				message: `Are you sure you want to delete ${itemName}? This action cannot be undone.`,
				confirmText: "Delete",
				cancelText: "Cancel",
			});

			if (!confirmed) {
				return false;
			}

			await updateEntity(entityType, item.id, { is_active: false });
			showToastSuccess(`${itemType} deleted successfully.`);
			return true;
		} catch (error) {
			showToastError(`Failed to delete ${itemName}. Please check your connection and try again.`);
			return false;
		}
	};
};
