import { EntityType, JamData, useDataContext } from "../contexts/DataContext";
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

export const useDeactivateHandler = (entityType: EntityType, nameKey: string | null, itemType = "item") => {
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

export const useActivateEntity = (entityType: EntityType, nameKey: string | null, itemType = "item") => {
	const { updateEntity } = useDataContext();
	const { showToastSuccess, showToastError } = useGlobalToast();

	return async (item: any): Promise<boolean> => {
		const itemName: string = getItemName(item, nameKey, itemType);

		try {
			await updateEntity(entityType, item.id, { is_active: true });
			showToastSuccess(`${itemType} activated successfully.`);
			return true;
		} catch (error) {
			showToastError(`Failed to activate ${itemName}. Please check your connection and try again.`);
			return false;
		}
	};
};

export const useDeactivateEntity = (entityType: EntityType, nameKey: string | null, itemType = "item") => {
	const { updateEntity } = useDataContext();
	const { showToastSuccess, showToastError } = useGlobalToast();

	return async (item: any): Promise<boolean> => {
		const itemName: string = getItemName(item, nameKey, itemType);

		try {
			await updateEntity(entityType, item.id, { is_active: false });
			showToastSuccess(`${itemType} deactivated successfully.`);
			return true;
		} catch (error) {
			showToastError(`Failed to deactivate ${itemName}. Please check your connection and try again.`);
			return false;
		}
	};
};

export const useSmartDeleteHandler = (
	entityType: EntityType,
	nameKey: string | null,
	itemType = "item",
	canDeactivate: ((item: JamData) => string | null) | null, // returns a string explaining why it can't be deleted, or empty string if it can be deleted
) => {
	const { deleteEntity, updateEntity } = useDataContext();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const { showDelete } = useAlert();

	return async (item: any): Promise<boolean> => {
		const itemName: string = getItemName(item, nameKey, itemType);

		let condition: string | null = null;
		if (canDeactivate) {
			condition = canDeactivate(item);
		}
		try {
			if (!condition) {
				const confirmed: boolean = await showDelete({
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
			} else {
				const confirmed: boolean = await showDelete({
					title: `Delete ${itemType}`,
					message: `${itemName} cannot be deleted due to ${condition} Do you want to deactivate it instead?`,
					confirmText: "Deactivate",
					cancelText: "Cancel",
				});
				if (!confirmed) {
					return false;
				}
				await updateEntity(entityType, item.id, { is_active: false });
				showToastSuccess(`${itemType} deactivated successfully.`);
				return true;
			}
		} catch (error) {
			showToastError(`Failed to delete ${itemName}. Please check your connection and try again.`);
			return false;
		}
	};
};
