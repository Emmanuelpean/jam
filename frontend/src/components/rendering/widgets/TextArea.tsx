import React, { JSX } from "react";
import { Form } from "react-bootstrap";
import { displayError, WidgetProps } from "./WidgetRenders";

export const renderTextarea = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	return (
		<>
			<Form.Control
				as="textarea"
				id={field.name}
				rows={field.rows || 3}
				name={field.name}
				value={value || ""}
				onChange={handleChange}
				placeholder={field.placeholder}
				isInvalid={!!error}
				className="optimized-textarea"
			/>
			{error && (
				<div className="invalid-feedback" id={`${field.name}-error-message`}>
					{displayError(error)}
				</div>
			)}
		</>
	);
};
