import { Form } from "react-bootstrap";
import "./UrlInput.css";
import { WidgetProps } from "./WidgetRenders";
import React, { JSX } from "react";
import { scraperApi } from "../../../services/Api";

export const renderUrlInputWidget = ({ field, value, handleChange, error, currentUser }: WidgetProps): JSX.Element => {
	const handleOpenUrl = () => {
		if (value && value.trim()) {
			let url = value.trim();
			if (!url.startsWith("http://") && !url.startsWith("https://")) {
				url = "https://" + url;
			}
			window.open(url, "_blank");
		}
	};

	const handleScrapeUrl = () => {
		if (value && value.trim() && currentUser?.toast_active && currentUser?.token) {
			let url = value.trim();
			if (!url.startsWith("http://") && !url.startsWith("https://")) {
				url = "https://" + url;
			}

			// LinkedIn job URL logic
			const match = url.match(/linkedin\.com\/jobs\/view\/(\d+)/);
			if (match && match[1]) {
				scraperApi.get(`linkedin/${match[1]}`, currentUser?.token);
				return;
			}

			// VeganJobs logic
			if (url.includes("veganjobs.com")) {
				console.log("here");
				const match = url.match(/veganjobs\.com\/job\/([^/]+)/);
				if (match && match[1]) {
					const result = scraperApi.get(`veganjobs/${match[1]}`, currentUser?.token);
					console.log(result);
					return;
				}
			}
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
			<button
				type="button"
				className={`url-scrape-button ${!currentUser?.toast_active || !value || !value.trim() ? "disabled" : ""}`}
				onClick={handleScrapeUrl}
				disabled={!currentUser?.toast_active || !value || !value.trim()}
				title={
					currentUser?.toast_active || !value || !value.trim()
						? "Scrape the URL"
						: "Scraping is disabled because TOAST is not active"
				}
			>
				<i className="bi bi-search"></i>
			</button>
		</div>
	);
};
