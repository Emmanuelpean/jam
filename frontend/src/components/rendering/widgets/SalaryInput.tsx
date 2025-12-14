import React, { JSX } from "react";
import { Form, InputGroup } from "react-bootstrap";
import { WidgetProps } from "./WidgetRenders";
import { Currency, DataContextValue, useDataContext } from "../../../contexts/DataContext";

export const SalaryInput = ({
	field,
	value,
	handleChange,
	error,
	currentUser,
	secondaryValue,
}: WidgetProps): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();
	const currencyCode: string | undefined = secondaryValue ? secondaryValue : currentUser?.default_currency;

	const currentSymbol: string =
		dataContext.currencies.filter((currency: Currency): boolean => currency.code === currencyCode)[0]?.symbol ||
		"N/A";

	return (
		<>
			<InputGroup>
				<InputGroup.Text>{currentSymbol}</InputGroup.Text>
				<Form.Control
					id={field.name}
					type="text"
					name={field.name}
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
