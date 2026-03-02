import { useCallback, useMemo } from "react";
import { useAuth } from "../contexts/AuthContext";
import { TableColumn } from "../components/rendering/view/TableColumns";
import { getDefaultColumns, getDefaultColumnKeys, resolveColumns } from "../components/DataTable/columnRegistry";
import { SortConfig } from "../components/DataTable/DataTable";

export interface ColumnConfig {
	visibleColumns: TableColumn[];
	allColumns: TableColumn[];
	columnOrder: string[];
	isDefault: boolean;
	savedSort: SortConfig | null;
	setColumnConfig: (keys: string[]) => Promise<void>;
	setSortConfig: (sort: SortConfig) => Promise<void>;
	resetToDefaults: () => Promise<void>;
}

export function useColumnConfig(entityType: string): ColumnConfig {
	const { currentUser, updateCurrentUser } = useAuth();

	const savedKeys: string[] | null = useMemo(() => {
		return currentUser?.preferences?.table_columns?.[entityType] ?? null;
	}, [currentUser, entityType]);

	const savedSort: SortConfig | null = useMemo(() => {
		const s = currentUser?.preferences?.table_sort?.[entityType];
		if (!s) return null;
		return { key: s.key, direction: s.direction as SortConfig["direction"] };
	}, [currentUser, entityType]);

	const allColumns = useMemo(() => getDefaultColumns(entityType), [entityType]);

	const defaultKeys = useMemo(() => getDefaultColumnKeys(entityType), [entityType]);

	const isDefault = savedKeys === null && savedSort === null;

	const columnOrder = savedKeys ?? defaultKeys;

	const visibleColumns = useMemo(() => {
		if (savedKeys === null) return allColumns;
		return resolveColumns(entityType, columnOrder);
	}, [savedKeys, allColumns, entityType, columnOrder]);

	const setColumnConfig = useCallback(
		async (keys: string[]) => {
			const existing = currentUser?.preferences?.table_columns ?? {};
			await updateCurrentUser({
				preferences: {
					table_columns: { ...existing, [entityType]: keys },
				},
			});
		},
		[currentUser, entityType, updateCurrentUser]
	);

	const setSortConfig = useCallback(
		async (sort: SortConfig) => {
			const existing = currentUser?.preferences?.table_sort ?? {};
			await updateCurrentUser({
				preferences: {
					table_sort: { ...existing, [entityType]: { key: sort.key, direction: sort.direction } },
				},
			});
		},
		[currentUser, entityType, updateCurrentUser]
	);

	const resetToDefaults = useCallback(async () => {
		const existingCols = currentUser?.preferences?.table_columns ?? {};
		const existingSort = currentUser?.preferences?.table_sort ?? {};
		const updatedCols = { ...existingCols };
		const updatedSort = { ...existingSort };
		delete updatedCols[entityType];
		delete updatedSort[entityType];
		await updateCurrentUser({
			preferences: {
				table_columns: Object.keys(updatedCols).length > 0 ? updatedCols : null,
				table_sort: Object.keys(updatedSort).length > 0 ? updatedSort : null,
			},
		});
	}, [currentUser, entityType, updateCurrentUser]);

	return {
		visibleColumns,
		allColumns,
		columnOrder,
		isDefault,
		savedSort,
		setColumnConfig,
		setSortConfig,
		resetToDefaults,
	};
}
