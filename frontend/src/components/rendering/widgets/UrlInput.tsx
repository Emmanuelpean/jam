import { Form } from "react-bootstrap";
import "./UrlInput.scss";
import { WidgetProps } from "./WidgetRenders";
import React, { JSX } from "react";
import { toKey } from "../../../utils/StringUtils";
import { Tooltip, TITLE_TOOLTIP_DELAY } from "../../Tooltip/Tooltip";

export const UrlInput = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	const handleOpenUrl = () => {
		if (value && value.trim()) {
			// Add protocol if missing
			let url: string = value.trim();
			if (!url.startsWith("http://") && !url.startsWith("https://")) {
				url = "https://" + url;
			}
			window.open(url, "_blank");
		}
	};

	return (
		<div className="url-input-wrapper">
			<Form.Control
				id={toKey(field.key)}
				name={toKey(field.key)}
				value={value || ""}
				onChange={handleChange}
				placeholder={field.placeholder || "Enter URL"}
				isInvalid={!!error}
				step={field.step}
				autoComplete={field.autoComplete}
				className="url-input-field"
				disabled={field.isDisabled}
			/>
			<Tooltip content="Open URL in new tab" delay={TITLE_TOOLTIP_DELAY}>
				<button
					type="button"
					className={`url-open-button ${!value || !value.trim() ? "disabled" : ""}`}
					onClick={handleOpenUrl}
					disabled={!value || !value.trim()}
				>
					<i className="bi bi-box-arrow-up-right"></i>
				</button>
			</Tooltip>
		</div>
	);
};
