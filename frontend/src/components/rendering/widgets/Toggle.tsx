import React, { JSX } from "react";
import { Form } from "react-bootstrap";
import { WidgetProps } from "./WidgetRenders";

export const Toggle = ({ field, value, handleChange }: WidgetProps): JSX.Element => {
	return (
		<Form.Check
			type="switch"
			id={field.name}
			name={field.name}
			checked={value || false}
			onChange={handleChange}
			label={field.label}
		/>
	);
};
