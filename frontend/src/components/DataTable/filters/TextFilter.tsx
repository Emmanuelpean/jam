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
		placeholder="Contains..."
		value={value.value}
		onChange={(e) => onChange({ type: "text", value: e.target.value })}
		className="form-control--sm"
	/>
);

export default TextFilter;
