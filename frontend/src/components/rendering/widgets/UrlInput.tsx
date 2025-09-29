import { Form } from "react-bootstrap";
import "./UrlInput.css";
import { WidgetProps } from "./WidgetRenders";
import React, { JSX } from "react";

export const renderUrlInputWidget = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	const handleOpenUrl = () => {
		if (value && value.trim()) {
			// Add protocol if missing
			let url = value.trim();
			if (!url.startsWith("http://") && !url.startsWith("https://")) {
				url = "https://" + url;
			}
			window.open(url, "_blank");
		}
	};

	return (
		<div className="url-input-wrapper">
			<Form.Control
				id={field.name}
				type={field.type || "url"}
				name={field.name}
				value={value || ""}
				onChange={handleChange}
				placeholder={field.placeholder || "Enter URL"}
				isInvalid={!!error}
				step={field.step}
				autoComplete={field.autoComplete}
				className="url-input-field"
			/>
			<button
				type="button"
				className={`url-open-button ${!value || !value.trim() ? "disabled" : ""}`}
				onClick={handleOpenUrl}
				disabled={!value || !value.trim()}
				title="Open URL in new tab"
			>
				<i className="bi bi-box-arrow-up-right"></i>
			</button>
		</div>
	);
};
