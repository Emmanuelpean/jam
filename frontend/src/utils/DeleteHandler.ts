import { useDataContext, EntityType } from "../contexts/DataContext";

export interface CreateDeleteHandlerProps {
	entityType: EntityType;
	showDelete: (config: any) => Promise<boolean>;
	showError: (config: any) => Promise<boolean>;
	nameKey?: string;
	itemType?: string;
}

const getItemName = (item: any, nameKey?: string, itemType?: string): string => {
	if (nameKey && nameKey !== "date") {
		return `"${item[nameKey]}"`;
	} else if (itemType) {
		return `this ${itemType}`;
	} else {
		return `this item`;
	}
};

export const useDeleteHandler = ({
	entityType,
	showDelete,
	showError,
	nameKey,
	itemType = "item",
}: CreateDeleteHandlerProps) => {
	const { deleteEntity } = useDataContext();

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
			return true;
		} catch (error) {
			await showError({
				message: `Failed to delete ${itemName}. Please check your connection and try again.`,
			});
			return false;
		}
	};
};

export const useActiveHandler = ({
	entityType,
	showDelete,
	showError,
	nameKey,
	itemType = "item",
}: CreateDeleteHandlerProps) => {
	const { updateEntity } = useDataContext();

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
			return true;
		} catch (error) {
			await showError({
				message: `Failed to delete ${itemName}. Please check your connection and try again.`,
			});
			return false;
		}
	};
};
