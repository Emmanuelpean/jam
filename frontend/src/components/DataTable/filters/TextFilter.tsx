import React, { JSX } from "react";
import { Form } from "react-bootstrap";
import { TextFilterValue } from "../FilterTypes";

interface Props {
	value: TextFilterValue;
	onChange: (v: TextFilterValue) => void;
}

const TextFilter = ({ value, onChange }: Props): JSX.Element => (
	<Form.Control
		type="text"
		size="sm"
		placeholder="Contains..."
		value={value.value}
		onChange={(e) => onChange({ type: "text", value: e.target.value })}
	/>
);

export default TextFilter;
