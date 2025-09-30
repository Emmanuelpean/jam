import { api } from "../services/Api";

export interface CreateDeleteHandlerProps {
	endpoint: string;
	token: string | null;
	showDelete: (config: any) => Promise<boolean>;
	showError: (config: any) => Promise<boolean>;
	removeItem?: (itemId: string | number) => void;
	setData?: React.Dispatch<React.SetStateAction<any[]>>;
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

export const createDeleteHandler = ({
	endpoint,
	token,
	showDelete,
	showError,
	removeItem,
	nameKey,
	itemType = "item",
}: CreateDeleteHandlerProps) => {
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
				return false; // User cancelled
			}

			await api.delete(`${endpoint}/${item.id}`, token);
			removeItem?.(item.id);
			return true;
		} catch (error) {
			await showError({
				message: `Failed to delete ${itemName}. Please check your connection and try again.`,
			});
			return false; // Failed to delete
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
}: CreateDeleteHandlerProps) => {
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
				return false; // User cancelled
			}

			await api.put(`${endpoint}/set_active/${item.id}`, { is_active: false }, token);
			removeItem?.(item.id);
			return true;
		} catch (error) {
			await showError({
				message: `Failed to delete ${itemName}. Please check your connection and try again.`,
			});
			return false;
		}
	};
};
