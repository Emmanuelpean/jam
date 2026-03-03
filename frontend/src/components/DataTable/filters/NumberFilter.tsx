import React, { JSX } from "react";
import { Form } from "react-bootstrap";
import { NumberFilterConfig, NumberFilterValue } from "../FilterTypes";

interface Props {
	config: NumberFilterConfig;
	value: NumberFilterValue;
	onChange: (v: NumberFilterValue) => void;
}

const NumberFilter = ({ config, value, onChange }: Props): JSX.Element => {
	const step = config.step ?? 1;

	return (
		<div className="filter-number-range">
			<Form.Control
				type="number"
				size="sm"
				placeholder="Min"
				step={step}
				value={value.min ?? ""}
				onChange={(e) =>
					onChange({ type: "number", min: e.target.value === "" ? null : Number(e.target.value), max: value.max })
				}
			/>
			<span className="filter-range-sep">–</span>
			<Form.Control
				type="number"
				size="sm"
				placeholder="Max"
				step={step}
				value={value.max ?? ""}
				onChange={(e) =>
					onChange({ type: "number", min: value.min, max: e.target.value === "" ? null : Number(e.target.value) })
				}
			/>
		</div>
	);
};

export default NumberFilter;
