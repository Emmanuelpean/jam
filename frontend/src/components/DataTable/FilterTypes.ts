import { SelectOption } from "../rendering/form/FormOptions";

// ---- Filter configuration (defined on each column) ----

export interface TextFilterConfig {
	type: "text";
}

export interface SelectFilterConfig {
	type: "select";
	options: SelectOption[];
}

export interface DateFilterConfig {
	type: "date";
}

export interface NumberFilterConfig {
	type: "number";
	min: number;
	max: number | ((ctx: any) => number);
	step?: number;
	display?: "slider" | "input";
	nullable?: boolean;
}

export interface ReferenceFilterConfig {
	type: "reference";
	// Key in DataContext (e.g. "companies", "locations")
	entityKey: string;
	// Field on the row item holding the FK (e.g. "company_id"). Supports array FKs too.
	valueField: string;
	// Field on the referenced entity to show as label (default: "name")
	labelKey?: string;
}

export type FilterConfig =
	| TextFilterConfig
	| SelectFilterConfig
	| DateFilterConfig
	| NumberFilterConfig
	| ReferenceFilterConfig;

// ---- Filter values (one per active column filter) ----

export interface TextFilterValue {
	type: "text";
	value: string;
}

export interface SelectFilterValue {
	type: "select";
	selected: string[];
}

export type DatePreset = "last7" | "last30" | "thisMonth" | "custom";

export interface DateFilterValue {
	type: "date";
	preset: DatePreset | null;
	from: string | null; // YYYY-MM-DD
	to: string | null;   // YYYY-MM-DD
}

export interface NumberFilterValue {
	type: "number";
	min: number | null;
	max: number | null;
	includeEmpty?: boolean;
}

export interface ReferenceFilterValue {
	type: "reference";
	selectedIds: string[];
}

export type FilterValue =
	| TextFilterValue
	| SelectFilterValue
	| DateFilterValue
	| NumberFilterValue
	| ReferenceFilterValue;

export type ActiveFilters = Record<string, FilterValue>;

// ---- Utility functions ----

export function isFilterActive(filter: FilterValue): boolean {
	switch (filter.type) {
		case "text":
			return filter.value.trim().length > 0;
		case "select":
			return filter.selected.length > 0;
		case "date":
			return filter.from !== null || filter.to !== null;
		case "number":
			return filter.min !== null || filter.max !== null || filter.includeEmpty === false;
		case "reference":
			return filter.selectedIds.length > 0;
	}
}

export function countActiveFilters(filters: ActiveFilters): number {
	return Object.values(filters).filter(isFilterActive).length;
}

export function createEmptyFilter(config: FilterConfig): FilterValue {
	switch (config.type) {
		case "text":
			return { type: "text", value: "" };
		case "select":
			return { type: "select", selected: [] };
		case "date":
			return { type: "date", preset: null, from: null, to: null };
		case "number":
			return { type: "number", min: null, max: null };
		case "reference":
			return { type: "reference", selectedIds: [] };
	}
}
