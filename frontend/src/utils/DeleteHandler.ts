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

interface EntityOperationConfig {
	entityType: EntityType;
	operation: (
		entityType: EntityType,
		id: number,
		data?: any
	) => Promise<null> | ApiResponsePromise<JamData>;
	successMessage: (entityTypeName: string) => string;
	errorMessage: (entityName: string) => string;
	confirmationConfig?: {
		title: (entityTypeName: string) => string;
		message: (entityName: string) => string;
	};
}

const useEntityOperation = (
	config: EntityOperationConfig
): ((item: JamData) => Promise<boolean>) => {
	const { entityType, operation, successMessage, errorMessage, confirmationConfig } = config;
	const { showToastSuccess, showToastError } = useGlobalToast();
	const { showDelete } = useAlert();
	const dataContext: DataContextValue = useDataContext();

	return async (item: JamData): Promise<boolean> => {
		const entityTypeName: string = entityTypeToGenericName(entityType);
		const entityName: string = entityTypeToName(entityType, dataContext)(item);

		if (confirmationConfig) {
			return await showDelete({
				title: confirmationConfig.title(entityTypeName),
				message: confirmationConfig.message(entityName),
				confirmText: "Delete",
				cancelText: "Cancel",
				onSuccess: async (): Promise<void> => {
					try {
						await operation(entityType, item.id, item);
						showToastSuccess(successMessage(entityTypeName));
					} catch (error) {
						showToastError(errorMessage(entityName));
						throw error; // Re-throw so confirm modal knows it failed
					}
				},
			});
		} else {
			try {
				await operation(entityType, item.id, item);
				showToastSuccess(successMessage(entityTypeName));
				return true;
			} catch (error) {
				showToastError(errorMessage(entityName));
				return false;
			}
		}
	};
};

export const useDeleteEntityConfirm = (
	entityType: EntityType
): ((item: JamData) => Promise<boolean>) => {
	const { deleteEntity } = useDataContext();
	return useEntityOperation({
		entityType: entityType,
		operation: (type: EntityType, id: number): Promise<any> => deleteEntity(type, id),
		successMessage: (typeName: string): string => `${typeName} deleted successfully.`,
		errorMessage: (name: string): string =>
			`Failed to delete "${name}". Please check your connection and try again.`,
		confirmationConfig: {
			title: (typeName: string): string => `Delete ${typeName}`,
			message: (name: string): string =>
				`Are you sure you want to delete "${name}"? This will delete it for all the entries it is associated with. This action cannot be undone.`,
		},
	});
};

export const useDeactivateEntityConfirm = (
	entityType: EntityType
): ((item: JamData) => Promise<boolean>) => {
	const { updateEntity } = useDataContext();
	return useEntityOperation({
		entityType: entityType,
		operation: (type: EntityType, id: number): ApiResponsePromise<JamData> =>
			updateEntity(type, id, { is_active: false }),
		successMessage: (typeName: string): string => `${typeName} deleted successfully.`,
		errorMessage: (name: string): string =>
			`Failed to delete "${name}". Please check your connection and try again.`,
		confirmationConfig: {
			title: (typeName: string): string => `Delete ${typeName}`,
			message: (name: string): string =>
				`Are you sure you want to delete "${name}"? This action cannot be undone.`,
		},
	});
};

export const useActivateEntity = (
	entityType: EntityType
): ((item: JamData) => Promise<boolean>) => {
	const { updateEntity } = useDataContext();
	return useEntityOperation({
		entityType: entityType,
		operation: (type: EntityType, id: number): ApiResponsePromise<JamData> =>
			updateEntity(type, id, { is_active: true }),
		successMessage: (typeName: string): string => `${typeName} activated successfully.`,
		errorMessage: (name: string): string =>
			`Failed to activate "${name}". Please check your connection and try again.`,
	});
};

export const useDeactivateEntity = (
	entityType: EntityType
): ((item: JamData) => Promise<boolean>) => {
	const { updateEntity } = useDataContext();
	return useEntityOperation({
		entityType: entityType,
		operation: (type: EntityType, id: number): ApiResponsePromise<JamData> =>
			updateEntity(type, id, { is_active: false }),
		successMessage: (typeName: string): string => `${typeName} deactivated successfully.`,
		errorMessage: (name: string): string =>
			`Failed to deactivate "${name}". Please check your connection and try again.`,
	});
};
