import { SelectOption } from "../rendering/form/FormOptions";

export interface FilterPill {
	key: string;
	label: string;
	summary: string;
	onRemove: () => void;
}

export interface TextFilterConfig {
	type: "text";
}

export interface SelectFilterConfig {
	type: "select";
	options: SelectOption[];
}

export interface DatePresetOption {
	key: DatePreset;
	label: string;
}

export interface DateFilterConfig {
	type: "date";
	presets?: DatePresetOption[];
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
	entityKey: string; // Key in DataContext (e.g. "companies", "locations")
	valueField: string; // Field on the row item holding the FK (e.g. "company_id"). Supports array FKs too.
	labelKey?: string; // Field on the referenced entity to show as label (default: "name")
}

export type FilterConfig =
	| TextFilterConfig
	| SelectFilterConfig
	| DateFilterConfig
	| NumberFilterConfig
	| ReferenceFilterConfig;

export interface TextFilterValue {
	type: "text";
	value: string;
}

export interface SelectFilterValue {
	type: "select";
	selected: string[];
}

export type DatePreset = "last7" | "last30" | "next7" | "next30" | "thisMonth" | "pastDeadline" | "custom";

export interface DateFilterValue {
	type: "date";
	preset: DatePreset | null;
	from: string | null; // YYYY-MM-DD
	to: string | null; // YYYY-MM-DD
}

export type NullFilter = "all" | "null" | "not_null";

export interface NumberFilterValue {
	type: "number";
	min: number | null;
	max: number | null;
	nullFilter?: NullFilter;
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

/** True when the filter actually narrows results — drives the dot indicator and active count. */
export function isFilterActive(filter: FilterValue): boolean {
	switch (filter.type) {
		case "text":
			return filter.value.trim().length > 0;
		case "select":
			return filter.selected.length > 0;
		case "date":
			return (filter.preset !== null && filter.preset !== "custom") || filter.from !== null || filter.to !== null;
		case "number":
			return filter.min !== null || filter.max !== null || (!!filter.nullFilter && filter.nullFilter !== "all");
		case "reference":
			return filter.selectedIds.length > 0;
	}
}

/** True when the user has made any selection — drives whether the value is kept in state. */
export function isFilterSelected(filter: FilterValue): boolean {
	if (filter.type === "date") return filter.preset !== null || filter.from !== null || filter.to !== null;
	return isFilterActive(filter);
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
