import { ActiveFilters, FilterConfig, FilterValue, isFilterActive } from "./FilterTypes";
import { TableColumn } from "../rendering/view/TableColumns";
import { DataContextValue, JamData } from "../../contexts/DataContext";
import { accessAttribute } from "../../utils/Utils";

type Filter = [string, FilterValue];

export function applyFilters(
	data: JamData[],
	filters: ActiveFilters,
	columns: TableColumn[],
	dataContext: DataContextValue
): JamData[] {
	const active: Filter[] = Object.entries(filters).filter(([, v]: Filter): boolean => isFilterActive(v));
	if (active.length === 0) return data;

	return data.filter((item: JamData): boolean =>
		active.every(([key, filterValue]: Filter): boolean => {
			const column: TableColumn | undefined = columns.find((c: TableColumn): boolean => c.key === key);
			if (!column?.filterConfig) return true;
			return matchesFilter(item, column, filterValue, dataContext);
		})
	);
}

function matchesFilter(
	item: JamData,
	column: TableColumn,
	filter: FilterValue,
	dataContext: DataContextValue
): boolean {
	switch (filter.type) {
		case "text": {
			if (!filter.value.trim()) return true;
			const val: any = getItemValue(item, column, dataContext);
			return val?.toString().toLowerCase().includes(filter.value.toLowerCase()) ?? false;
		}

		case "select": {
			if (filter.selected.length === 0) return true;
			const val: any = getItemValue(item, column, dataContext);
			if (val == null) return false;
			return filter.selected.includes(String(val));
		}

		case "date": {
			if (!filter.from && !filter.to) return true;
			const val: any = getItemValue(item, column, dataContext);
			if (!val) return false;
			const dateStr: string = new Date(String(val)).toISOString().split("T")[0]!;
			if (filter.from && dateStr < filter.from) return false;
			return !(filter.to && dateStr > filter.to);
		}

		case "number": {
			const val: any = getItemValue(item, column, dataContext);
			const isEmpty: boolean = val == null || val === "" || isNaN(Number(val));

			// Handle null filter
			if (filter.nullFilter === "null") return isEmpty;
			if (filter.nullFilter === "not_null" && isEmpty) return false;

			if (isEmpty) return filter.min === null && filter.max === null;
			if (filter.min === null && filter.max === null) return true;
			const num: number = Number(val);
			if (filter.min !== null && num < filter.min) return false;
			return !(filter.max !== null && num > filter.max);
		}

		case "reference": {
			if (filter.selectedIds.length === 0) return true;
			const config: FilterConfig = column.filterConfig!;
			if (config.type !== "reference") return true;
			const raw: any = (item as any)[config.valueField];
			if (raw == null) return false;
			// Support array FKs (e.g. interviewers, contacts)
			if (Array.isArray(raw)) {
				return raw.some((id: number): boolean => filter.selectedIds.includes(String(id)));
			}
			return filter.selectedIds.includes(String(raw));
		}
	}
}

function getItemValue(item: JamData, column: TableColumn, dataContext: DataContextValue): any {
	// For reference columns use the FK field directly
	if (column.filterConfig?.type === "reference") {
		return (item as any)[(column.filterConfig as any).valueField];
	}
	// Use sortField function if present (resolves display-friendly value)
	if (typeof column.sortField === "function") return column.sortField(item, dataContext);
	if (typeof column.sortField === "string") return (item as any)[column.sortField];
	// Fall back to dot-notation access via the column key
	return accessAttribute(item, column.key);
}
