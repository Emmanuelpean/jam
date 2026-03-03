import React, { JSX } from "react";
import { Form } from "react-bootstrap";
import { SelectFilterConfig, SelectFilterValue } from "../FilterTypes";

interface Props {
	config: SelectFilterConfig;
	value: SelectFilterValue;
	onChange: (v: SelectFilterValue) => void;
}

const SelectFilter = ({ config, value, onChange }: Props): JSX.Element => {
	const toggle = (optValue: string) => {
		const selected = value.selected.includes(optValue)
			? value.selected.filter((v) => v !== optValue)
			: [...value.selected, optValue];
		onChange({ type: "select", selected });
	};

	return (
		<div className="filter-checkbox-list">
			{config.options.map((opt) => (
				<Form.Check
					key={opt.value}
					type="checkbox"
					id={`filter-sel-${opt.value}`}
					label={opt.label}
					checked={value.selected.includes(String(opt.value))}
					onChange={() => toggle(String(opt.value))}
					className="filter-checkbox-item"
				/>
			))}
		</div>
	);
};

export default SelectFilter;
