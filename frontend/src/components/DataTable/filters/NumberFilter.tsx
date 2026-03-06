import React, { JSX, useCallback, useMemo } from "react";
import { Form } from "react-bootstrap";
import { NullFilter, NumberFilterConfig, NumberFilterValue } from "../FilterTypes";
import "./NumberFilter.scss";

interface Props {
	config: NumberFilterConfig;
	value: NumberFilterValue;
	onChange: (v: NumberFilterValue) => void;
	dataContext?: any;
}

function resolveMax(config: NumberFilterConfig, dataContext?: any): number {
	if (typeof config.max === "function") {
		return config.max(dataContext) || 1;
	}
	return config.max;
}

const NumberSlider = ({ config, value, onChange, dataContext }: Props): JSX.Element => {
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
		<div className="filter-range-slider">
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
					className="filter-range-slider-input"
				/>
				<input
					type="range"
					min={rangeMin}
					max={rangeMax}
					step={step}
					value={currentMax}
					onChange={handleMaxChange}
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

const NumberInputs = ({ config, value, onChange }: Props): JSX.Element => {
	const step = config.step ?? 1;

	return (
		<div className="filter-number-range">
			<Form.Control
				type="number"
				placeholder="Min"
				step={step}
				value={value.min ?? ""}
				onChange={(e) =>
					onChange({ type: "number", min: e.target.value === "" ? null : Number(e.target.value), max: value.max })
				}
				className="form-control--sm"
			/>
			<span className="filter-range-sep">–</span>
			<Form.Control
				type="number"
				placeholder="Max"
				step={step}
				value={value.max ?? ""}
				onChange={(e) =>
					onChange({ type: "number", min: value.min, max: e.target.value === "" ? null : Number(e.target.value) })
				}
				className="form-control--sm"
			/>
		</div>
	);
};

const nullFilterOptions: { value: NullFilter; label: string }[] = [
	{ value: "all", label: "All" },
	{ value: "not_null", label: "Not null" },
	{ value: "null", label: "Null" },
];

const NumberFilter = ({ config, value, onChange, dataContext }: Props): JSX.Element => {
	const display = config.display ?? "input";
	const currentNullFilter = value.nullFilter ?? "all";

	const handleRangeChange = (v: NumberFilterValue) => {
		onChange({ ...v, nullFilter: value.nullFilter });
	};

	const sliderProps = { config, value, onChange: handleRangeChange, dataContext };

	return (
		<>
			{display === "slider" ? <NumberSlider {...sliderProps} /> : <NumberInputs {...sliderProps} />}
			{config.nullable && (
				<div className="filter-null-buttons">
					{nullFilterOptions.map((opt) => (
						<button
							key={opt.value}
							type="button"
							className={`filter-null-btn${currentNullFilter === opt.value ? " active" : ""}`}
							onClick={() => onChange({ ...value, nullFilter: opt.value === "all" ? undefined : opt.value })}
						>
							{opt.label}
						</button>
					))}
				</div>
			)}
		</>
	);
};

export default NumberFilter;
