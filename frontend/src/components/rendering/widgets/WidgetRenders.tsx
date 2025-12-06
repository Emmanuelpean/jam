import { Form } from "react-bootstrap";
import { renderStarRating } from "./StarRating";
import { renderSalaryInput } from "./SalaryInput";
import { renderTextarea } from "./TextArea";
import { renderDateLocal, renderDateTimeLocal } from "./Datetime";
import { renderPasswordInput } from "./PasswordInput";
import { renderCheckbox } from "./Checkbox";
import { RenderSelect, SelectWidgetPreviewConfig } from "./SelectWidget";
import { ModalFormField } from "../form/FormRenders";
import React, { JSX } from "react";
import { HelpBubble } from "./HelpBubble";
import { renderUrlInputWidget } from "./UrlInput";
import { CurrentUser } from "../../../contexts/AuthContext";

export interface SyntheticEvent {
	target: {
		name: string;
		value: any;
		type?: string;
		checked?: boolean;
	};
}

export interface Errors {
	[key: string]: string | null;
}

export interface WidgetProps {
	field: ModalFormField;
	value: any;
	handleChange: (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent) => void;
	error?: string | null;
	secondaryValue?: string | null;
	currentUser?: CurrentUser | null;
	previewConfig?: SelectWidgetPreviewConfig | null;
	data?: any;
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
				disabled={field.isDisabled}
			/>
		</>
	);
};

export const FormField = (
	field: ModalFormField,
	formData: any,
	handleChange: (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent) => void,
	errors: Errors,
	currentUser?: CurrentUser | null,
) => {
	const value: any = formData[field.name];
	const secondaryValue: any = field.secondaryName ? formData[field.secondaryName] : null;
	const error: string | null | undefined = errors[field.name];
	const previewConfig = field.previewConfig;

	const widgetProps: WidgetProps = {
		field,
		value,
		handleChange,
		error,
		secondaryValue,
		currentUser,
		previewConfig,
		data: formData,
	};

	if (field.type === "checkbox") {
		return (
			<Form.Group className="mb-4" id={`${field.name}-form-group`}>
				{renderCheckbox(widgetProps)}
				{error && (
					<div className="invalid-feedback d-block" id={`${field.name}-error-message`}>
						{displayError(error)}
					</div>
				)}
			</Form.Group>
		);
	}

	return (
		<Form.Group className="mb-4" id={`${field.name}-form-group`}>
			<Form.Label>
				{field.icon && <i className={`${field.icon} me-2 text-muted`}></i>}
				{field.label}
				{"required" in field && field.required && <span className="text-danger">*</span>}
				{field.helpText && <HelpBubble helpText={field.helpText} />}
			</Form.Label>
			{(() => {
				switch (field.type) {
					case "textarea":
						return renderTextarea(widgetProps);

					case "select":
					case "multiselect":
						return <RenderSelect {...widgetProps} />;

					case "datetime-local":
						return renderDateTimeLocal(widgetProps);

					case "date":
						return renderDateLocal(widgetProps);

					case "password":
						return renderPasswordInput(widgetProps);

					case "salary":
						return renderSalaryInput(widgetProps);

					case "rating":
						return renderStarRating(widgetProps);

					case "url":
						return renderUrlInputWidget(widgetProps);

					default:
						return renderDefaultInput(widgetProps);
				}
			})()}
			{error && (
				<div className="invalid-feedback d-block" id={`${field.name}-error-message`}>
					{displayError(error)}
				</div>
			)}
		</Form.Group>
	);
};
