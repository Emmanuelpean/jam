import React, { JSX } from "react";
import { Form } from "react-bootstrap";
import { WidgetProps } from "./WidgetRenders";
import { toKey } from "../../../utils/StringUtils";

export const Toggle = ({ field, value, handleChange }: WidgetProps): JSX.Element => {
	return (
		<Form.Check
			type="switch"
			id={toKey(field.name)}
			name={toKey(field.name)}
			checked={value || false}
			onChange={handleChange}
			label={field.label}
		/>
	);
};
