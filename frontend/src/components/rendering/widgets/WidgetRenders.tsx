import { Form } from "react-bootstrap";
import { StarRating } from "./StarRating";
import { SalaryInput } from "./SalaryInput";
import { Textarea } from "./TextArea";
import { LocalDatetimeInput } from "./Datetime";
import { PasswordInput } from "./PasswordInput";
import { Checkbox } from "./Checkbox";
import { SelectInput, SelectWidgetPreviewConfig } from "./SelectWidget";
import { ModalFormField } from "../form/FormRenders";
import React, { JSX } from "react";
import { HelpBubble } from "../../HelpBubble/HelpBubble";
import { UrlInput } from "./UrlInput";
import { CurrentUser } from "../../../contexts/AuthContext";
import { Toggle } from "./Toggle";
import { FavouriteStar } from "./FavouriteStar";
import get from "lodash/get";
import { toKey } from "../../../utils/StringUtils";

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

export const DefaultInput = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	return (
		<>
			<Form.Control
				id={toKey(field.name)}
				type={field.type || "text"}
				name={toKey(field.name)}
				key={toKey(field.name)}
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

export const renderFormField = (
	field: ModalFormField,
	formData: any,
	handleChange: (event: React.ChangeEvent<HTMLInputElement> | SyntheticEvent) => void,
	errors: Errors,
	currentUser?: CurrentUser | null
) => {
	const value: any = get(formData, field.name);
	const secondaryValue: any = field.secondaryName ? get(formData, field.secondaryName) : null;
	const error: string | null | undefined = get(errors, field.name);
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
			<Form.Group className="mb-3" id={`${field.name}-form-group`}>
				<Checkbox {...widgetProps} />
				{error && (
					<div className="invalid-feedback d-block" id={`${field.name}-error-message`}>
						{displayError(error)}
					</div>
				)}
			</Form.Group>
		);
	}
	if (field.type === "toggle") {
		return (
			<Form.Group className="mb-3" id={`${field.name}-form-group`}>
				<Toggle {...widgetProps} />
				{error && (
					<div className="invalid-feedback d-block" id={`${field.name}-error-message`}>
						{displayError(error)}
					</div>
				)}
			</Form.Group>
		);
	}

	return (
		<Form.Group className="mb-3" id={`${field.name}-form-group`}>
			{field.label && (
				<Form.Label>
					{field.icon && <i className={`${field.icon} me-2 text-muted`} aria-hidden="true" />}
					{field.label}
					{"required" in field && field.required && <span className="text-danger">*</span>}
					{field.helpText && <HelpBubble helpText={field.helpText} />}
				</Form.Label>
			)}
			{(() => {
				switch (field.type) {
					case "textarea":
						return <Textarea {...widgetProps} />;

					case "select":
					case "multiselect":
						return <SelectInput {...widgetProps} />;

					case "datetime-local":
						return <LocalDatetimeInput {...widgetProps} inputType="datetime-local" />;

					case "date":
						return <LocalDatetimeInput {...widgetProps} inputType="date" />;

					case "password":
						return <PasswordInput {...widgetProps} />;

					case "salary":
						return <SalaryInput {...widgetProps} />;

					case "rating":
						return <StarRating {...widgetProps} />;

					case "url":
						return <UrlInput {...widgetProps} />;

					case "star_toggle":
						return <FavouriteStar {...widgetProps} />;

					default:
						return <DefaultInput {...widgetProps} />;
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
