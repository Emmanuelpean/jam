import React, { JSX, useRef } from "react";
import { Form } from "react-bootstrap";
import { SyntheticEvent, WidgetProps } from "./WidgetRenders";
import "./Datetime.scss";
import { toKey } from "../../../utils/StringUtils";
import { Tooltip, TITLE_TOOLTIP_DELAY } from "../../Tooltip/Tooltip";

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
	const inputRef = useRef<HTMLInputElement>(null);

	const setCurrentValue = (e: React.MouseEvent<HTMLElement>): void => {
		e.preventDefault();
		e.stopPropagation();
		const syntheticEvent: SyntheticEvent = {
			target: {
				name: toKey(field.key),
				value: inputType === "datetime-local" ? formatDateTime() : formatDateTime(new Date(), true),
			},
		};
		handleChange(syntheticEvent);
	};

	const clearValue = (e: React.MouseEvent<HTMLElement>): void => {
		e.preventDefault();
		e.stopPropagation();
		handleChange({ target: { name: toKey(field.key), value: null } });
	};

	const openPicker = (e: React.MouseEvent<HTMLElement>): void => {
		e.preventDefault();
		e.stopPropagation();
		inputRef.current?.showPicker();
	};

	let formattedValue: string = "";
	if (value) {
		formattedValue = inputType === "datetime-local" ? formatDateTime(value) : formatDateTime(value, true);
	}

	return (
		<div className="datetime-input-wrapper">
			<Form.Control
				ref={inputRef}
				id={toKey(field.key)}
				type={inputType}
				name={toKey(field.key)}
				value={formattedValue}
				onChange={handleChange}
				isInvalid={!!error}
				className={`datetime-input-with-icon${!formattedValue ? " datetime-empty" : ""}`}
				disabled={field.isDisabled}
			/>
			{formattedValue && !field.isDisabled && (
				<Tooltip content="Clear" delay={TITLE_TOOLTIP_DELAY}>
					<i
						className="bi bi-x datetime-embedded-icon datetime-clear-icon"
						onClick={clearValue}
						id={toKey(field.key) + "_clear"}
					></i>
				</Tooltip>
			)}
			<Tooltip content="Open picker" delay={TITLE_TOOLTIP_DELAY}>
				<i
					className="bi bi-calendar datetime-embedded-icon datetime-calendar-icon"
					onClick={openPicker}
					id={toKey(field.key) + "_open_picker"}
				></i>
			</Tooltip>
			<Tooltip
				content={inputType === "datetime-local" ? "Set to current date and time" : "Set to current date"}
				delay={TITLE_TOOLTIP_DELAY}
			>
				<i
					className="bi bi-clock datetime-embedded-icon"
					onClick={setCurrentValue}
					id={toKey(field.key) + "_set_current"}
				></i>
			</Tooltip>
		</div>
	);
};
