import React, { JSX } from "react";
import { Form } from "react-bootstrap";
import { formatDate, formatDateTime } from "../../../utils/TimeUtils";
import { SyntheticEvent, WidgetProps } from "./WidgetRenders";
import "./Datetime.css";

type LocalInputType = "datetime-local" | "date";

interface LocalInputProps extends WidgetProps {
	inputType: LocalInputType;
}

/**
 * Generic renderer for datetime-local or date input
 */
export const renderLocalInput = ({ field, value, handleChange, error, inputType }: LocalInputProps): JSX.Element => {
	const setCurrentValue = (e: React.MouseEvent<HTMLElement>): void => {
		e.preventDefault();
		e.stopPropagation();
		const syntheticEvent: SyntheticEvent = {
			target: {
				name: field.name,
				value: inputType === "datetime-local" ? formatDateTime() : formatDate(new Date()),
			},
		};
		handleChange(syntheticEvent);
	};

	let formattedValue: string = "";
	if (value) {
		formattedValue = inputType === "datetime-local" ? formatDateTime(value) : formatDate(value);
	}

	return (
		<div className="datetime-input-wrapper">
			<Form.Control
				id={field.name}
				type={inputType}
				name={field.name}
				value={formattedValue}
				onChange={handleChange}
				isInvalid={!!error}
				className="datetime-input-with-icon"
			/>
			<i
				className={`bi bi-clock datetime-embedded-icon`}
				onClick={setCurrentValue}
				title={inputType === "datetime-local" ? "Set to current date and time" : "Set to current date"}
			></i>
		</div>
	);
};

export const renderDateTimeLocal = (props: WidgetProps): JSX.Element =>
	renderLocalInput({ ...props, inputType: "datetime-local" });

export const renderDateLocal = (props: WidgetProps): JSX.Element => renderLocalInput({ ...props, inputType: "date" });
