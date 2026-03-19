import React, { JSX } from "react";
import { Form } from "react-bootstrap";
import { TextFilterValue } from "../FilterTypes";

interface Props {
	columnKey?: string;
	value: TextFilterValue;
	onChange: (v: TextFilterValue) => void;
}

const TextFilter = ({ columnKey, value, onChange }: Props): JSX.Element => (
	<div className="filter-clearable-input">
		<Form.Control
			id={columnKey ? `filter-input-${columnKey}` : undefined}
			type="text"
			placeholder="Contains..."
			value={value.value}
			onChange={(e) => onChange({ type: "text", value: e.target.value })}
			className="form-control--sm"
		/>
		{value.value && (
			<button
				type="button"
				className="filter-input-clear-btn"
				onClick={() => onChange({ type: "text", value: "" })}
				aria-label="Clear"
			>
				<i className="bi bi-x" />
			</button>
		)}
	</div>
);

export default TextFilter;
