import {
	DataContextValue,
	EntityType,
	entityTypeToGenericName,
	entityTypeToName,
	JamData,
	useDataContext,
} from "../contexts/DataContext";
import { useGlobalToast } from "../hooks/useNotificationToast";
import { useAlert } from "../contexts/AlertContext";
import { ApiResponsePromise } from "../services/api/Base";

const useEntityOperation = (
	entityType: EntityType,
	operation: (entityType: EntityType, id: number, data?: any) => Promise<void> | ApiResponsePromise<JamData>,
	successMessage: (entityTypeName: string) => string,
	errorMessage: (entityName: string) => string,
	confirmationConfig?: {
		title: (entityTypeName: string) => string;
		message: (entityName: string) => string;
	},
) => {
	const { showToastSuccess, showToastError } = useGlobalToast();
	const { showDelete } = useAlert();
	const dataContext: DataContextValue = useDataContext();

	return async (item: JamData, data?: any): Promise<boolean> => {
		const entityTypeName: string = entityTypeToGenericName(entityType);
		const entityName: string = entityTypeToName(entityType, dataContext)(item);

		try {
			if (confirmationConfig) {
				const confirmed = await showDelete({
					title: confirmationConfig.title(entityTypeName),
					message: confirmationConfig.message(entityName),
					confirmText: "Delete",
					cancelText: "Cancel",
				});

				if (!confirmed) {
					return false;
				}
			}

			await operation(entityType, item.id, data);
			showToastSuccess(successMessage(entityTypeName));
			return true;
		} catch (error) {
			showToastError(errorMessage(entityName));
			return false;
		}
	};
};

export const useDeleteEntity = (entityType: EntityType) => {
	const { deleteEntity } = useDataContext();
	return useEntityOperation(
		entityType,
		(type: EntityType, id: number): Promise<void> => deleteEntity(type, id),
		(typeName: string): string => `${typeName} deleted successfully.`,
		(name: string): string => `Failed to delete ${name}. Please check your connection and try again.`,
		{
			title: (typeName: string): string => `Delete ${typeName}`,
			message: (name: string): string => `Are you sure you want to delete ${name}? This action cannot be undone.`,
		},
	);
};

export const useDeactivateHandler = (entityType: EntityType) => {
	const { updateEntity } = useDataContext();
	return useEntityOperation(
		entityType,
		(type: EntityType, id: number): ApiResponsePromise<JamData> => updateEntity(type, id, { is_active: false }),
		(typeName: string): string => `${typeName} deleted successfully.`,
		(name: string): string => `Failed to delete ${name}. Please check your connection and try again.`,
		{
			title: (typeName: string): string => `Delete ${typeName}`,
			message: (name: string): string => `Are you sure you want to delete ${name}? This action cannot be undone.`,
		},
	);
};

export const useActivateEntity = (entityType: EntityType) => {
	const { updateEntity } = useDataContext();
	return useEntityOperation(
		entityType,
		(type: EntityType, id: number): ApiResponsePromise<JamData> => updateEntity(type, id, { is_active: true }),
		(typeName: string): string => `${typeName} activated successfully.`,
		(name: string): string => `Failed to activate ${name}. Please check your connection and try again.`,
	);
};

export const useDeactivateEntity = (entityType: EntityType) => {
	const { updateEntity } = useDataContext();
	return useEntityOperation(
		entityType,
		(type: EntityType, id: number): ApiResponsePromise<JamData> => updateEntity(type, id, { is_active: false }),
		(typeName: string): string => `${typeName} deactivated successfully.`,
		(name: string): string => `Failed to deactivate ${name}. Please check your connection and try again.`,
	);
};
