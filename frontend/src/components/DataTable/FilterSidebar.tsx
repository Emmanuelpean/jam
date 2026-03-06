import React, { JSX, useMemo } from "react";
import { Button } from "react-bootstrap";
import { TableColumn } from "../rendering/view/TableColumns";
import { ActiveFilters, createEmptyFilter, FilterValue, countActiveFilters, isFilterActive } from "./FilterTypes";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import TextFilter from "./filters/TextFilter";
import SelectFilter from "./filters/SelectFilter";
import DateFilter from "./filters/DateFilter";
import NumberFilter from "./filters/NumberFilter";
import ReferenceFilter from "./filters/ReferenceFilter";
import "./FilterSidebar.scss";

// ---- Filter section per-column ----

interface FilterSectionProps {
	column: TableColumn;
	value: FilterValue | undefined;
	onChange: (v: FilterValue) => void;
	dataContext: DataContextValue;
}

const FilterSection = ({ column, value, onChange, dataContext }: FilterSectionProps): JSX.Element => {
	const config = column.filterConfig!;
	const active = value ? isFilterActive(value) : false;
	const current = value ?? createEmptyFilter(config);

	return (
		<div className={`filter-section${active ? " filter-section--active" : ""}`}>
			<label className="filter-section-label">
				{column.label}
				{active && <i className="bi bi-circle-fill filter-active-dot" />}
			</label>
			<div className="filter-section-body">
				{config.type === "text" && <TextFilter value={current as any} onChange={onChange} />}
				{config.type === "select" && (
					<SelectFilter config={config} value={current as any} onChange={onChange} />
				)}
				{config.type === "date" && <DateFilter config={config} value={current as any} onChange={onChange} />}
				{config.type === "number" && (
					<NumberFilter config={config} value={current as any} onChange={onChange} dataContext={dataContext} />
				)}
				{config.type === "reference" && (
					<ReferenceFilter
						config={config}
						value={current as any}
						onChange={onChange}
						dataContext={dataContext}
					/>
				)}
			</div>
		</div>
	);
};

// ---- Main sidebar ----

interface FilterSidebarProps {
	isOpen: boolean;
	onClose: () => void;
	columns: TableColumn[];
	filters: ActiveFilters;
	onFiltersChange: (f: ActiveFilters) => void;
}

const FilterSidebar = ({ isOpen, onClose, columns, filters, onFiltersChange }: FilterSidebarProps): JSX.Element => {
	const dataContext = useDataContext();
	const filterableColumns = useMemo(() => columns.filter((c) => c.filterConfig), [columns]);
	const activeCount = countActiveFilters(filters);

	const handleChange = (key: string, val: FilterValue) => {
		const updated = { ...filters };
		if (isFilterActive(val)) {
			updated[key] = val;
		} else {
			delete updated[key];
		}
		onFiltersChange(updated);
	};

	return (
		<div className={`filter-sidebar${isOpen ? " open" : ""}`}>
			<div className="filter-sidebar-header">
				<h6 className="mb-0">
					<i className="bi bi-funnel me-2" />
					Filters
					{activeCount > 0 && <span className="filter-sidebar-count">{activeCount}</span>}
				</h6>
				<button type="button" className="btn-close" onClick={onClose} aria-label="Close" />
			</div>

			<div className="filter-sidebar-body">
				{filterableColumns.length === 0 ? (
					<p className="text-muted text-center small py-3">No filterable columns.</p>
				) : (
					filterableColumns.map((col) => (
						<FilterSection
							key={col.key}
							column={col}
							value={filters[col.key]}
							onChange={(v) => handleChange(col.key, v)}
							dataContext={dataContext}
						/>
					))
				)}
			</div>

			<div className="filter-sidebar-footer">
				<Button style={{ width: "100%" }} onClick={() => onFiltersChange({})} disabled={activeCount === 0}>
					<i className="bi bi-x-circle me-1" />
					Clear all filters
				</Button>
			</div>
		</div>
	);
};

export default FilterSidebar;
