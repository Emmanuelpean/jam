import React, { JSX, useCallback, useMemo } from "react";
import { Form } from "react-bootstrap";
import { NullFilter, NumberFilterConfig, NumberFilterValue } from "../FilterTypes";
import "./NumberFilter.scss";
import ClearButton from "../ClearButton";

interface Props {
	columnKey?: string;
	config: NumberFilterConfig;
	value: NumberFilterValue;
	onChange: (v: NumberFilterValue) => void;
	dataContext?: any;
	disabled?: boolean;
}

function resolveMax(config: NumberFilterConfig, dataContext?: any): number {
	if (typeof config.max === "function") {
		return config.max(dataContext) || 1;
	}
	return config.max;
}

const NumberSlider = ({ columnKey, config, value, onChange, dataContext, disabled }: Props): JSX.Element => {
	const rangeMin = config.min;
	const rangeMax = useMemo(() => resolveMax(config, dataContext), [config, dataContext]);
	const step = config.step ?? 1;
	const currentMin = value.min ?? rangeMin;
	const currentMax = value.max ?? rangeMax;

	const toPercent = (v: number) => ((v - rangeMin) / (rangeMax - rangeMin)) * 100;

	const handleMinChange = useCallback(
		(e: React.ChangeEvent<HTMLInputElement>) => {
			const v = Number(e.target.value);
			const newMin = Math.min(v, currentMax);
			onChange({
				type: "number",
				min: newMin <= rangeMin ? null : newMin,
				max: currentMax >= rangeMax ? null : currentMax,
			});
		},
		[currentMax, rangeMin, rangeMax, onChange]
	);

	const handleMaxChange = useCallback(
		(e: React.ChangeEvent<HTMLInputElement>) => {
			const v = Number(e.target.value);
			const newMax = Math.max(v, currentMin);
			onChange({
				type: "number",
				min: currentMin <= rangeMin ? null : currentMin,
				max: newMax >= rangeMax ? null : newMax,
			});
		},
		[currentMin, rangeMin, rangeMax, onChange]
	);

	return (
		<div className={`filter-range-slider${disabled ? " filter-range-slider--disabled" : ""}`}>
			<div className="filter-range-slider-track">
				<div
					className="filter-range-slider-fill"
					style={{
						left: `${toPercent(currentMin)}%`,
						width: `${toPercent(currentMax) - toPercent(currentMin)}%`,
					}}
				/>
				<input
					type="range"
					min={rangeMin}
					max={rangeMax}
					step={step}
					value={currentMin}
					onChange={handleMinChange}
					disabled={disabled}
					className="filter-range-slider-input"
					style={{ zIndex: currentMax >= rangeMax ? 1 : undefined }}
				/>
				<input
					type="range"
					min={rangeMin}
					max={rangeMax}
					step={step}
					value={currentMax}
					onChange={handleMaxChange}
					disabled={disabled}
					className="filter-range-slider-input"
				/>
			</div>
			<div className="filter-range-slider-labels">
				<span>{currentMin}</span>
				<span>{currentMax}</span>
			</div>
		</div>
	);
};

const NumberInputs = ({ columnKey, config, value, onChange, disabled }: Props): JSX.Element => {
	const step = config.step ?? 1;

	const hasValue = value.min !== null || value.max !== null;

	return (
		<div className="filter-number-range">
			<Form.Control
				id={columnKey ? `filter-num-min-${columnKey}` : undefined}
				type="number"
				placeholder="Min"
				step={step}
				value={value.min ?? ""}
				onChange={(e) =>
					onChange({
						type: "number",
						min: e.target.value === "" ? null : Number(e.target.value),
						max: value.max,
					})
				}
				className="form-control--sm"
				disabled={disabled}
			/>
			<span className="filter-range-sep">–</span>
			<Form.Control
				id={columnKey ? `filter-num-max-${columnKey}` : undefined}
				type="number"
				placeholder="Max"
				step={step}
				value={value.max ?? ""}
				onChange={(e) =>
					onChange({
						type: "number",
						min: value.min,
						max: e.target.value === "" ? null : Number(e.target.value),
					})
				}
				className="form-control--sm"
				disabled={disabled}
			/>
			{hasValue && !disabled && (
				<ClearButton onClick={() => onChange({ type: "number", min: null, max: null })} size="sm" />
			)}
		</div>
	);
};

const nullFilterOptions: { value: NullFilter; label: string }[] = [
	{ value: "all", label: "All" },
	{ value: "not_null", label: "Not null" },
	{ value: "null", label: "Null" },
];

const NumberFilter = ({ columnKey, config, value, onChange, dataContext }: Props): JSX.Element => {
	const display = config.display ?? "input";
	const currentNullFilter = value.nullFilter ?? "all";

	const handleRangeChange = (v: NumberFilterValue) => {
		onChange({ ...v, nullFilter: value.nullFilter });
	};

	const isNullOnly = currentNullFilter === "null";
	const sliderProps = { columnKey, config, value, onChange: handleRangeChange, dataContext, disabled: isNullOnly };

	return (
		<div className={`filter-number-wrapper${config.nullable ? " filter-number-wrapper--with-null" : ""}`}>
			<div className="filter-number-range-col">
				{display === "slider" ? <NumberSlider {...sliderProps} /> : <NumberInputs {...sliderProps} />}
			</div>
			{config.nullable && (
				<div className="filter-null-buttons">
					{nullFilterOptions.map((opt) => (
						<button
							key={opt.value}
							id={columnKey ? `filter-null-${opt.value}-${columnKey}` : undefined}
							type="button"
							className={`filter-null-btn${currentNullFilter === opt.value ? " active" : ""}`}
							onClick={() =>
								onChange({
									...value,
									nullFilter: opt.value === "all" ? undefined : opt.value,
								})
							}
						>
							{opt.label}
						</button>
					))}
				</div>
			)}
		</div>
	);
};

export default NumberFilter;
