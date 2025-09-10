import React, { JSX, useState } from "react";
import { Form } from "react-bootstrap";
import { displayError, WidgetProps } from "./WidgetRenders";

const PasswordInput = ({ field, value, handleChange, error }: WidgetProps) => {
	const [showPassword, setShowPassword] = useState<boolean>(false);

	return (
		<>
			<div className="position-relative">
				<Form.Control
					type={showPassword ? "text" : "password"}
					id={field.name}
					name={field.name}
					placeholder={field.placeholder || "Enter your password"}
					value={value || ""}
					onChange={handleChange}
					size={"lg"}
					isInvalid={!!error}
					autoComplete={field.autoComplete || "current-password"}
					style={{ paddingRight: "50px" }}
				/>
				<button
					type="button"
					className={`password-toggle-btn ${showPassword ? "" : "show-slash"}`}
					onClick={() => setShowPassword(!showPassword)}
					tabIndex={0}
				>
					<i className="bi bi-eye"></i>
				</button>
			</div>
			{field.helpText && !error && <Form.Text className="text-muted">{field.helpText}</Form.Text>}
		</>
	);
};

export const renderPasswordInput = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	return <PasswordInput field={field} value={value} handleChange={handleChange} error={error} />;
};
