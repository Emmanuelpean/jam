import React, { JSX } from "react";
import { Form } from "react-bootstrap";
import { formatDateTime } from "../../../utils/TimeUtils";
import { SyntheticEvent } from "./WidgetRenders";
import { displayError, WidgetProps } from "./WidgetRenders";
import "./Datetime.css";

export const renderDateTimeLocal = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	const setCurrentTime = (e: React.MouseEvent<HTMLElement>): void => {
		e.preventDefault();
		e.stopPropagation();
		const syntheticEvent: SyntheticEvent = {
			target: {
				name: field.name,
				value: formatDateTime(),
			},
		};
		handleChange(syntheticEvent);
	};

	// Use formatDateTime for formatting
	const formattedValue = formatDateTime(value);

	return (
		<>
			<div className="datetime-input-wrapper">
				<Form.Control
					id={field.name}
					type="datetime-local"
					name={field.name}
					value={formattedValue}
					onChange={handleChange}
					isInvalid={!!error}
					className="datetime-input-with-icon"
				/>
				<i
					className="bi bi-clock datetime-embedded-icon"
					onClick={setCurrentTime}
					title="Set to current date and time"
				></i>
			</div>
			{error && (
				<div className="invalid-feedback d-block" id={`${field.name}-error-message`}>
					{displayError(error)}
				</div>
			)}
		</>
	);
};
