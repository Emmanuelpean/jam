import { Form } from "react-bootstrap";
import { renderStarRating } from "./StarRating";
import { renderSalaryInput } from "./SalaryInput";
import { renderTextarea } from "./TextArea";
import { renderDateTimeLocal } from "./Datetime";
import { renderPasswordInput } from "./PasswordInput";
import { renderCheckbox } from "./Checkbox";
import { renderSelect } from "./SelectWidget";
import { FormField } from "../form/FormRenders";
import React, { JSX } from "react";

export interface SyntheticEvent {
	target: {
		name: string;
		value: any;
	};
}

export interface Errors {
	[key: string]: string | null;
}

export interface WidgetProps {
	field: FormField;
	value: any;
	handleChange: (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent) => void;
	error?: string | null;
}

export const displayError = (errorMessage: string | null): JSX.Element[] | null => {
	if (!errorMessage) return null;
	return errorMessage.split("\n").map((line: string, index: number): JSX.Element => <div key={index}>{line}</div>);
};

export const renderDefaultInput = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	return (
		<>
			<Form.Control
				id={field.name}
				type={field.type || "text"}
				name={field.name}
				value={value || ""}
				onChange={handleChange}
				placeholder={field.placeholder}
				isInvalid={!!error}
				step={field.step}
				autoComplete={field.autoComplete}
			/>
			{error && (
				<div className="invalid-feedback" id={`${field.name}-error-message`}>
					{displayError(error)}
				</div>
			)}
		</>
	);
};

export const renderFormField = (
	field: FormField,
	formData: any,
	handleChange: (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent) => void,
	errors: Errors,
) => {
	const value: any = formData[field.name];
	const error: string | null | undefined = errors[field.name];

	const widgetProps: WidgetProps = {
		field,
		value,
		handleChange,
		error,
	};

	if (field.type === "checkbox") {
		return <Form.Group className="mb-4">{renderCheckbox(widgetProps)}</Form.Group>;
	}

	return (
		<Form.Group className="mb-4">
			<Form.Label>
				{field.icon && <i className={`${field.icon} me-2 text-muted`}></i>}
				{field.label}
				{"required" in field && field.required && <span className="text-danger">*</span>}
			</Form.Label>
			{(() => {
				switch (field.type) {
					case "textarea":
						return renderTextarea(widgetProps);

					case "select":
					case "multiselect":
						return renderSelect(widgetProps);

					case "datetime-local":
						return renderDateTimeLocal(widgetProps);

					case "password":
						return renderPasswordInput(widgetProps);

					case "salary":
						return renderSalaryInput(widgetProps);

					case "rating":
						return renderStarRating(widgetProps);

					default:
						return renderDefaultInput(widgetProps);
				}
			})()}
		</Form.Group>
	);
};
