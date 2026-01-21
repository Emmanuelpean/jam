import React, { JSX } from "react";
import { Form } from "react-bootstrap";
import { WidgetProps } from "./WidgetRenders";
import "./TextArea.scss";
import { toKey } from "../../../utils/StringUtils";

export const Textarea = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	return (
		<>
			<Form.Control
				as="textarea"
				id={toKey(field.name)}
				rows={field.rows || 3}
				name={toKey(field.name)}
				value={value || ""}
				onChange={handleChange}
				placeholder={field.placeholder}
				isInvalid={!!error}
				className="optimized-textarea"
				disabled={field.isDisabled}
			/>
		</>
	);
};
