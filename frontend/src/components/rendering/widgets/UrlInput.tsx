import { Form } from "react-bootstrap";
import "./UrlInput.scss";
import { WidgetProps } from "./WidgetRenders";
import React, { JSX } from "react";
import { toKey } from "../../../utils/StringUtils";

export const UrlInput = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	const charCount = field.maxChars ? (value || "").length : 0;
	const isOverLimit = field.maxChars ? charCount > field.maxChars : false;

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
		<>
			<div className="url-input-wrapper">
				<Form.Control
					id={toKey(field.key)}
					name={toKey(field.key)}
					value={value || ""}
					onChange={handleChange}
					placeholder={field.placeholder || "Enter URL"}
					isInvalid={!!error || isOverLimit}
					step={field.step}
					autoComplete={field.autoComplete}
					className="url-input-field"
					disabled={field.isDisabled}
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
			{isOverLimit && field.maxChars && (
				<Form.Text className="text-danger">
					{charCount} / {field.maxChars} characters
				</Form.Text>
			)}
		</>
	);
};
