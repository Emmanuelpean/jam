import React, { JSX, useMemo } from "react";
import { Button } from "react-bootstrap";
import { TableColumn } from "../rendering/view/TableColumns";
import {
	ActiveFilters,
	createEmptyFilter,
	FilterValue,
	countActiveFilters,
	isFilterActive,
	FilterConfig,
	TextFilterValue,
	SelectFilterValue,
	DateFilterValue,
	NumberFilterValue,
	ReferenceFilterValue,
} from "./FilterTypes";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import TextFilter from "./filters/TextFilter";
import SelectFilter from "./filters/SelectFilter";
import DateFilter from "./filters/DateFilter";
import NumberFilter from "./filters/NumberFilter";
import ReferenceFilter from "./filters/ReferenceFilter";
import "./FilterSidebar.scss";

interface FilterSectionProps {
	column: TableColumn;
	value: FilterValue | undefined;
	onChange: (v: FilterValue) => void;
	dataContext: DataContextValue;
}

const FilterSection = ({ column, value, onChange, dataContext }: FilterSectionProps): JSX.Element => {
	const config: FilterConfig = column.filterConfig!;
	const active: boolean = value ? isFilterActive(value) : false;
	const current: FilterValue = value ?? createEmptyFilter(config);

	return (
		<div id={`filter-section-${column.key}`} className={`filter-section${active ? " filter-section--active" : ""}`}>
			<label className="filter-section-label">
				{column.label}
				{active && <i className="bi bi-circle-fill filter-active-dot" />}
			</label>
			<div className="filter-section-body">
				{config.type === "text" && (
					<TextFilter columnKey={column.key} value={current as TextFilterValue} onChange={onChange} />
				)}
				{config.type === "select" && (
					<SelectFilter
						columnKey={column.key}
						config={config}
						value={current as SelectFilterValue}
						onChange={onChange}
					/>
				)}
				{config.type === "date" && (
					<DateFilter
						columnKey={column.key}
						config={config}
						value={current as DateFilterValue}
						onChange={onChange}
					/>
				)}
				{config.type === "number" && (
					<NumberFilter
						columnKey={column.key}
						config={config}
						value={current as NumberFilterValue}
						onChange={onChange}
						dataContext={dataContext}
					/>
				)}
				{config.type === "reference" && (
					<ReferenceFilter
						columnKey={column.key}
						config={config}
						value={current as ReferenceFilterValue}
						onChange={onChange}
						dataContext={dataContext}
					/>
				)}
				{column.sidebarExtra}
			</div>
		</div>
	);
};

interface FilterSidebarProps {
	isOpen: boolean;
	onClose: () => void;
	columns: TableColumn[];
	filters: ActiveFilters;
	onFiltersChange: (f: ActiveFilters) => void;
}

const FilterSidebar = ({ isOpen, onClose, columns, filters, onFiltersChange }: FilterSidebarProps): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();
	const filterableColumns: TableColumn[] = useMemo(
		(): TableColumn[] => columns.filter((c: TableColumn): FilterConfig | undefined => c.filterConfig),
		[columns]
	);
	const activeCount: number = countActiveFilters(filters);

	const handleChange = (key: string, val: FilterValue): void => {
		const updated = { ...filters };
		if (isFilterActive(val)) {
			updated[key] = val;
		} else {
			delete updated[key];
		}
		onFiltersChange(updated);
	};

	return (
		<div id="filter-sidebar" className={`filter-sidebar${isOpen ? " open" : ""}`}>
			<div className="filter-sidebar-header">
				<h6 className="mb-0">
					<i className="bi bi-funnel me-2" />
					Filters
					{activeCount > 0 && <span className="filter-sidebar-count">{activeCount}</span>}
				</h6>
				<button
					id="filter-close-btn"
					type="button"
					className="btn-close"
					onClick={onClose}
					aria-label="Close"
				/>
			</div>

			<div className="filter-sidebar-body">
				{filterableColumns.length === 0 ? (
					<p className="text-muted text-center small py-3">No filterable columns.</p>
				) : (
					filterableColumns.map(
						(col: TableColumn): JSX.Element => (
							<FilterSection
								key={col.key}
								column={col}
								value={filters[col.key]}
								onChange={(v: FilterValue): void => handleChange(col.key, v)}
								dataContext={dataContext}
							/>
						)
					)
				)}
			</div>

			<div className="filter-sidebar-footer">
				<Button
					id="filter-clear-btn"
					style={{ width: "100%" }}
					onClick={(): void => onFiltersChange({})}
					disabled={activeCount === 0}
				>
					<i className="bi bi-x-circle me-1" />
					Clear all filters
				</Button>
			</div>
		</div>
	);
};

export default FilterSidebar;
