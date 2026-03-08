import React, { JSX, useState } from "react";
import { Form } from "react-bootstrap";
import { WidgetProps } from "./WidgetRenders";
import "./PasswordInput.scss";
import { toKey } from "../../../utils/StringUtils";

export const PasswordInput = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	const [showPassword, setShowPassword] = useState<boolean>(false);

	return (
		<>
			<div className="position-relative">
				<Form.Control
					type={showPassword ? "text" : "password"}
					id={toKey(field.name)}
					name={toKey(field.name)}
					placeholder={field.placeholder || "Enter your password"}
					value={value || ""}
					onChange={handleChange}
					size={"lg"}
					isInvalid={!!error}
					autoComplete={field.autoComplete || "current-password"}
					style={{ paddingRight: "45px" }}
					disabled={field.isDisabled}
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
			{/*{field.helpText && !error && <Form.Text className="text-muted">{field.helpText}</Form.Text>}*/}
		</>
	);
};
