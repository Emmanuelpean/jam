import React, { JSX } from "react";
import { Form } from "react-bootstrap";
import { DateFilterConfig, DateFilterValue, DatePreset, DatePresetOption } from "../FilterTypes";

interface Props {
	columnKey: string;
	config: DateFilterConfig;
	value: DateFilterValue;
	onChange: (v: DateFilterValue) => void;
}

const DEFAULT_PRESETS: DatePresetOption[] = [
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
	if (preset === "next7") {
		const d = new Date(now);
		d.setDate(d.getDate() + 7);
		return { type: "date", preset, from: today, to: d.toISOString().split("T")[0] ?? null };
	}
	if (preset === "next30") {
		const d = new Date(now);
		d.setDate(d.getDate() + 30);
		return { type: "date", preset, from: today, to: d.toISOString().split("T")[0] ?? null };
	}
	if (preset === "thisMonth") {
		const from = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split("T")[0] ?? null;
		const to = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split("T")[0] ?? null;
		return { type: "date", preset, from, to };
	}
	if (preset === "pastDeadline") {
		const yesterday = new Date(now);
		yesterday.setDate(yesterday.getDate() - 1);
		return { type: "date", preset, from: null, to: yesterday.toISOString().split("T")[0] ?? null };
	}
	// custom — keep existing range, just switch preset
	return { type: "date", preset: "custom", from: null, to: null };
}

const DateFilter = ({ config, value, onChange }: Props): JSX.Element => {
	const presets = config.presets ?? DEFAULT_PRESETS;
	const showCustomRange: boolean = value.preset === "custom";

	const handleDateChange = (field: "from" | "to", raw: string) => {
		const val = raw || null;
		const updated: DateFilterValue = { ...value, preset: "custom", [field]: val };
		if (updated.from && updated.to && updated.from > updated.to) {
			const tmp = updated.from;
			updated.from = updated.to;
			updated.to = tmp;
		}
		onChange(updated);
	};

	return (
		<div className="filter-date">
			<div className="filter-date-presets">
				{presets.map((p) => (
					<button
						key={p.key}
						type="button"
						className={`filter-date-preset-btn${value.preset === p.key ? " active" : ""}`}
						onClick={() =>
						value.preset === p.key
							? onChange({ type: "date", preset: null, from: null, to: null })
							: onChange(applyPreset(p.key))
					}
					>
						{p.label}
					</button>
				))}
			</div>

			{showCustomRange && (
				<div className="filter-date-range" key={`${value.from}-${value.to}`}>
					<Form.Control
						type="date"
						defaultValue={value.from ?? ""}
						onChange={(e) => handleDateChange("from", e.target.value)}
						className="form-control--sm"
					/>
					<span className="filter-range-sep">to</span>
					<Form.Control
						type="date"
						defaultValue={value.to ?? ""}
						onChange={(e) => handleDateChange("to", e.target.value)}
						className="form-control--sm"
					/>
				</div>
			)}
		</div>
	);
};

export default DateFilter;
