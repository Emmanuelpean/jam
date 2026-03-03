import React, { JSX } from "react";
import { Form } from "react-bootstrap";
import { DateFilterValue, DatePreset } from "../FilterTypes";

interface Props {
	value: DateFilterValue;
	onChange: (v: DateFilterValue) => void;
}

const PRESETS: { key: DatePreset; label: string }[] = [
	{ key: "last7", label: "Last 7 days" },
	{ key: "last30", label: "Last 30 days" },
	{ key: "thisMonth", label: "This month" },
	{ key: "custom", label: "Custom" },
];

function applyPreset(preset: DatePreset): DateFilterValue {
	const now = new Date();
	const today = now.toISOString().split("T")[0] ?? null;

	if (preset === "last7") {
		const d = new Date(now);
		d.setDate(d.getDate() - 7);
		return { type: "date", preset, from: d.toISOString().split("T")[0] ?? null, to: today };
	}
	if (preset === "last30") {
		const d = new Date(now);
		d.setDate(d.getDate() - 30);
		return { type: "date", preset, from: d.toISOString().split("T")[0] ?? null, to: today };
	}
	if (preset === "thisMonth") {
		const from = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split("T")[0] ?? null;
		return { type: "date", preset, from, to: today };
	}
	// custom — keep existing range, just switch preset
	return { type: "date", preset: "custom", from: null, to: null };
}

const DateFilter = ({ value, onChange }: Props): JSX.Element => {
	const showCustomRange = value.preset === "custom" || value.preset === null;

	return (
		<div className="filter-date">
			<div className="filter-date-presets">
				{PRESETS.map((p) => (
					<button
						key={p.key}
						type="button"
						className={`filter-date-preset-btn${value.preset === p.key ? " active" : ""}`}
						onClick={() => onChange(applyPreset(p.key))}
					>
						{p.label}
					</button>
				))}
			</div>

			{showCustomRange && (
				<div className="filter-date-range">
					<Form.Control
						type="date"
						size="sm"
						value={value.from ?? ""}
						onChange={(e) =>
							onChange({ ...value, preset: "custom", from: e.target.value || null })
						}
					/>
					<span className="filter-range-sep">to</span>
					<Form.Control
						type="date"
						size="sm"
						value={value.to ?? ""}
						onChange={(e) =>
							onChange({ ...value, preset: "custom", to: e.target.value || null })
						}
					/>
				</div>
			)}
		</div>
	);
};

export default DateFilter;
