import React, { JSX } from "react";
import { FilterPill } from "./FilterTypes";
import "./FilterPillsRow.scss";

interface Props {
	filterPills: FilterPill[];
	onClear: () => void;
}

const FilterPillsRow = ({ filterPills, onClear }: Props): JSX.Element | null => {
	if (filterPills.length === 0) return null;
	return (
		<tr>
			<td className="filter-pills-row" style={{ gridColumn: "1 / -1" }}>
				<div className="filter-pills-row-inner">
					<div className="header-filter-pills">
						{filterPills.map(
							(pill: FilterPill): JSX.Element => (
								<span key={pill.key} className="header-filter-pill">
									<span className="header-filter-pill-label">{pill.label}:</span>
									<span className="header-filter-pill-value">{pill.summary}</span>
									<button
										type="button"
										className="header-filter-pill-remove"
										onClick={pill.onRemove}
										aria-label={`Remove ${pill.label} filter`}
									>
										<i className="bi bi-x" />
									</button>
								</span>
							)
						)}
					</div>
					<button type="button" className="filter-pills-clear-btn" onClick={onClear}>
						Clear
					</button>
				</div>
			</td>
		</tr>
	);
};

export default FilterPillsRow;