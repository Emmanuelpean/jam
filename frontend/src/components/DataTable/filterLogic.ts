import { ActiveFilters, FilterValue, isFilterActive } from "./FilterTypes";
import { TableColumn } from "../rendering/view/TableColumns";
import { DataContextValue, JamData } from "../../contexts/DataContext";
import { accessAttribute } from "../../utils/Utils";

export function applyFilters(
	data: JamData[],
	filters: ActiveFilters,
	columns: TableColumn[],
	dataContext: DataContextValue
): JamData[] {
	const active = Object.entries(filters).filter(([, v]) => isFilterActive(v));
	if (active.length === 0) return data;

	return data.filter((item) =>
		active.every(([key, filterValue]) => {
			const column = columns.find((c) => c.key === key);
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
			const val = getItemValue(item, column, dataContext);
			return val?.toString().toLowerCase().includes(filter.value.toLowerCase()) ?? false;
		}

		case "select": {
			if (filter.selected.length === 0) return true;
			const val = getItemValue(item, column, dataContext);
			if (val == null) return false;
			return filter.selected.includes(String(val));
		}

		case "date": {
			if (!filter.from && !filter.to) return true;
			const val = getItemValue(item, column, dataContext);
			if (!val) return false;
			const dateStr = new Date(String(val)).toISOString().split("T")[0]!;
			if (filter.from && dateStr < filter.from) return false;
			if (filter.to && dateStr > filter.to) return false;
			return true;
		}

		case "number": {
			if (filter.min === null && filter.max === null && filter.includeEmpty !== false) return true;
			const val = getItemValue(item, column, dataContext);
			const isEmpty = val == null || val === "" || isNaN(Number(val));
			if (isEmpty) {
				if (filter.includeEmpty === true) return true;
				if (filter.includeEmpty === false) return false;
				return filter.min === null && filter.max === null;
			}
			const num = Number(val);
			if (filter.min !== null && num < filter.min) return false;
			if (filter.max !== null && num > filter.max) return false;
			return true;
		}

		case "reference": {
			if (filter.selectedIds.length === 0) return true;
			const config = column.filterConfig!;
			if (config.type !== "reference") return true;
			const raw = (item as any)[config.valueField];
			if (raw == null) return false;
			// Support array FKs (e.g. interviewers, contacts)
			if (Array.isArray(raw)) {
				return raw.some((id) => filter.selectedIds.includes(String(id)));
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
