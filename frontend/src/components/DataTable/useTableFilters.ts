import React, { Dispatch, SetStateAction, useMemo, useRef, useState } from "react";
import { FilterPill } from "../../pages/PageHeader/PageHeader";
import { TableColumn } from "../rendering/view/TableColumns";
import { DataContextValue } from "../../contexts/DataContext";
import { ColumnConfig } from "../../hooks/useColumnConfig";
import {
	ActiveFilters,
	countActiveFilters,
	DatePreset,
	FilterValue,
	isFilterActive,
	ReferenceFilterConfig,
	SelectFilterConfig,
} from "./FilterTypes";

interface UseTableFiltersOptions {
	enableColumnConfig: boolean;
	columnConfig: ColumnConfig;
	effectiveColumns: TableColumn[];
	dataContext: DataContextValue;
}

export interface UseTableFiltersReturn {
	filters: ActiveFilters;
	setFilters: Dispatch<SetStateAction<ActiveFilters>>;
	filterSidebarOpen: boolean;
	setFilterSidebarOpen: Dispatch<SetStateAction<boolean>>;
	filterSidebarRef: React.RefObject<HTMLDivElement>;
	filterPills: FilterPill[];
	activeFilterCount: number;
}

export const useTableFilters = ({
	enableColumnConfig,
	columnConfig,
	effectiveColumns,
	dataContext,
}: UseTableFiltersOptions): UseTableFiltersReturn => {
	const [filters, setFilters] = useState<ActiveFilters>({});
	const [filterSidebarOpen, setFilterSidebarOpen] = useState<boolean>(false);
	const filterSidebarRef = useRef<HTMLDivElement>(null);

	const filterPills: FilterPill[] = useMemo(() => {
		return Object.entries(filters)
			.filter(([, val]: [string, FilterValue]): boolean => isFilterActive(val))
			.flatMap(([key, val]: [string, FilterValue]) => {
				const allCols = enableColumnConfig ? columnConfig.allColumns : effectiveColumns;
				const col = allCols.find((c) => c.key === key);
				if (!col) return [];
				let summary = "";
				switch (val.type) {
					case "text":
						summary = `"${val.value}"`;
						break;
					case "select": {
						const cfg = col.filterConfig as SelectFilterConfig;
						const names = val.selected.map((v) => cfg.options.find((o) => o.value === v)?.label ?? v);
						summary = names.slice(0, 2).join(", ");
						if (names.length > 2) summary += ` +${names.length - 2}`;
						break;
					}
					case "date": {
						if (val.preset === "custom" && !val.from && !val.to) return [];
						const presetLabels: Record<DatePreset, string> = {
							last7: "Last 7 days",
							last30: "Last 30 days",
							next7: "Next 7 days",
							next30: "Next 30 days",
							thisMonth: "This month",
							pastDeadline: "Past deadline",
							custom: "",
						};
						if (val.preset && val.preset !== "custom") {
							summary = presetLabels[val.preset];
						} else if (val.from && val.to) {
							summary = `${val.from} \u2013 ${val.to}`;
						} else if (val.from) {
							summary = `From ${val.from}`;
						} else {
							summary = `Until ${val.to}`;
						}
						break;
					}
					case "number": {
						const parts: string[] = [];
						if (val.min !== null && val.max !== null) parts.push(`${val.min} \u2013 ${val.max}`);
						else if (val.min !== null) parts.push(`\u2265 ${val.min}`);
						else if (val.max !== null) parts.push(`\u2264 ${val.max}`);
						if (val.nullFilter === "not_null") parts.push("Not null");
						else if (val.nullFilter === "null") parts.push("Null only");
						summary = parts.join(", ");
						break;
					}
					case "reference": {
						const cfg = col.filterConfig as ReferenceFilterConfig;
						const entities: any[] = (dataContext as any)[cfg.entityKey] ?? [];
						const lk = cfg.labelKey ?? "name";
						const names = val.selectedIds.map((id) => {
							const e = entities.find((en) => String(en.id) === id);
							return e ? String(e[lk] ?? e.id) : id;
						});
						summary = names.slice(0, 2).join(", ");
						if (names.length > 2) summary += ` +${names.length - 2}`;
						break;
					}
				}
				return [
					{
						key,
						label: col.label,
						summary,
						onRemove: () =>
							setFilters((prev) => {
								const u = { ...prev };
								delete u[key];
								return u;
							}),
					},
				];
			});
	}, [filters, effectiveColumns, dataContext, enableColumnConfig, columnConfig.allColumns]);

	return {
		filters,
		setFilters,
		filterSidebarOpen,
		setFilterSidebarOpen,
		filterSidebarRef,
		filterPills,
		activeFilterCount: countActiveFilters(filters),
	};
};
