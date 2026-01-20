import React, { JSX } from "react";
import { Spinner } from "react-bootstrap";
import "./ProgressOverlay.scss";

interface ProgressOverlayProps {
	show: boolean;
	title?: string;
	message?: string | React.ReactNode;
	spinnerVariant?: "primary" | "secondary" | "success" | "danger" | "warning" | "info" | "light" | "dark";
}

export const ProgressOverlay: React.FC<ProgressOverlayProps> = ({
	show,
	title,
	message,
	spinnerVariant = "primary",
}: ProgressOverlayProps): JSX.Element => {
	return (
		<div className={`progress-overlay ${show ? "show" : ""}`}>
			<div className="progress-overlay-card">
				<Spinner animation="border" variant={spinnerVariant} style={{ width: "3rem", height: "3rem" }} />

				{title && (
					<h5 className="mt-3 mb-0 text-center" style={{ fontWeight: 600 }}>
						{title}
					</h5>
				)}

				{message && (
					<div className="mt-4 text-center text-muted">
						{typeof message === "string" ? <p className="mb-0">{message}</p> : message}
					</div>
				)}
			</div>
		</div>
	);
};
