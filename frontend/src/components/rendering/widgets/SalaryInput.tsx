import React, { JSX } from "react";
import { Form, InputGroup } from "react-bootstrap";
import { displayError, WidgetProps } from "./WidgetRenders";

export const renderSalaryInput = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	return (
		<>
			<InputGroup>
				<InputGroup.Text>£</InputGroup.Text>
				<Form.Control
					id={field.name}
					type="number"
					name={field.name}
					value={value || ""}
					onChange={handleChange}
					placeholder={field.placeholder}
					isInvalid={!!error}
					step={field.step}
					min="0"
					className={error ? "is-invalid" : ""}
				/>
				<InputGroup.Text>/Year</InputGroup.Text>
			</InputGroup>
			{error && (
				<div className="invalid-feedback d-block" id={`${field.name}-error-message`}>
					{displayError(error)}
				</div>
			)}
		</>
	);
};
