import React, { JSX } from "react";
import { Form } from "react-bootstrap";
import { SyntheticEvent, WidgetProps } from "./WidgetRenders";
import "./Datetime.scss";
import { toKey } from "../../../utils/StringUtils";

export const formatDateTime = (datetime?: string | Date, dateOnly: boolean = false): string => {
	if (!datetime) {
		datetime = new Date();
	} else {
		datetime = new Date(datetime);
	}
	const year = datetime.getFullYear();
	const month = String(datetime.getMonth() + 1).padStart(2, "0");
	const day = String(datetime.getDate()).padStart(2, "0");
	if (dateOnly) {
		return `${year}-${month}-${day}`;
	} else {
		const hours = String(datetime.getHours()).padStart(2, "0");
		const minutes = String(datetime.getMinutes()).padStart(2, "0");
		return `${year}-${month}-${day}T${hours}:${minutes}`;
	}
};

type LocalInputType = "datetime-local" | "date";

interface LocalInputProps extends WidgetProps {
	inputType: LocalInputType;
}

export const LocalDatetimeInput = ({
	field,
	value,
	handleChange,
	error,
	inputType = "datetime-local",
}: LocalInputProps): JSX.Element => {
	const setCurrentValue = (e: React.MouseEvent<HTMLElement>): void => {
		e.preventDefault();
		e.stopPropagation();
		const syntheticEvent: SyntheticEvent = {
			target: {
				name: toKey(field.name),
				value: inputType === "datetime-local" ? formatDateTime() : formatDateTime(new Date(), true),
			},
		};
		handleChange(syntheticEvent);
	};

	let formattedValue: string = "";
	if (value) {
		formattedValue = inputType === "datetime-local" ? formatDateTime(value) : formatDateTime(value, true);
	}

	return (
		<div className="datetime-input-wrapper">
			<Form.Control
				id={toKey(field.name)}
				type={inputType}
				name={toKey(field.name)}
				value={formattedValue}
				onChange={handleChange}
				isInvalid={!!error}
				className="datetime-input-with-icon"
				disabled={field.isDisabled}
			/>
			<i
				className={`bi bi-clock datetime-embedded-icon`}
				onClick={setCurrentValue}
				id={field.name + "_set_current"}
				title={inputType === "datetime-local" ? "Set to current date and time" : "Set to current date"}
			></i>
		</div>
	);
};
