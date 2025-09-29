import { api } from "../services/Api";

export interface CreateGenericDeleteHandlerProps {
	endpoint: string;
	token: string | null;
	showDelete: (config: any) => Promise<boolean>;
	showError: (config: any) => Promise<boolean>;
	removeItem?: (itemId: string | number) => void;
	setData?: React.Dispatch<React.SetStateAction<any[]>>;
	nameKey?: string;
	itemType?: string;
}

const getItemName = (item: any, nameKey?: string): string => {
	if (!nameKey) {
		return `this ${nameKey}`;
	} else if (nameKey !== "date") {
		return `"${item[nameKey]}"`;
	} else {
		return `this item`;
	}
};

export const createDeleteHandler = ({
	endpoint,
	token,
	showDelete,
	showError,
	removeItem,
	nameKey,
	itemType = "item",
}: CreateGenericDeleteHandlerProps) => {
	return async (item: any): Promise<void> => {
		const itemName = getItemName(item, nameKey);

		try {
			await showDelete({
				title: `Delete ${itemType}`,
				message: `Are you sure you want to delete ${itemName}? This action cannot be undone.`,
				confirmText: "Delete",
				cancelText: "Cancel",
			});

			await api.delete(`${endpoint}/${item.id}`, token);
			removeItem?.(item.id);
		} catch (error) {
			if (error !== false) {
				await showError({
					message: `Failed to delete ${itemName}. Please check your connection and try again.`,
				});
			}
		}
	};
};

export const createActiveHandler = ({
	endpoint,
	token,
	showDelete,
	showError,
	removeItem,
	nameKey,
	itemType = "item",
}: CreateGenericDeleteHandlerProps) => {
	return async (item: any): Promise<void> => {
		const itemName = getItemName(item, nameKey);

		try {
			await showDelete({
				title: `Delete ${itemType}`,
				message: `Are you sure you want to delete ${itemName}? This action cannot be undone.`,
				confirmText: "Delete",
				cancelText: "Cancel",
			});

			await api.put(`${endpoint}/set_active/${item.id}`, { is_active: false }, token);
			removeItem?.(item.id);
		} catch (error) {
			if (error !== false) {
				await showError({
					message: `Failed to delete ${itemName}. Please check your connection and try again.`,
				});
			}
		}
	};
};
