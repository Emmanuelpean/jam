import React, { JSX } from "react";
import { Form, InputGroup } from "react-bootstrap";
import { WidgetProps } from "./WidgetRenders";
import { Currency } from "../../../services/schemas/Others";
import { useStaticData } from "../../../contexts/StaticDataContext";
import { toKey } from "../../../utils/StringUtils";

export const SalaryInput = ({
	field,
	value,
	handleChange,
	error,
	currentUser,
	secondaryValue,
}: WidgetProps): JSX.Element => {
	const { currencies } = useStaticData();
	const currencyCode: string | undefined = secondaryValue
		? secondaryValue
		: currentUser?.preferences.default_currency;

	const currentSymbol: string =
		currencies.filter((currency: Currency): boolean => currency.code === currencyCode)[0]?.symbol ||
		"N/A";

	return (
		<>
			<InputGroup style={{ minWidth: "250px" }}>
				<InputGroup.Text>{currentSymbol}</InputGroup.Text>
				<Form.Control
					id={toKey(field.key)}
					type="text"
					name={toKey(field.key)}
					value={value || ""}
					onChange={handleChange}
					placeholder={field.placeholder}
					isInvalid={!!error}
					step={field.step}
					min="0"
					className={error ? "is-invalid" : ""}
					disabled={field.isDisabled}
				/>
				<InputGroup.Text>/Year</InputGroup.Text>
			</InputGroup>
		</>
	);
};
