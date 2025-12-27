import React, { JSX } from "react";

interface LoadingSpinnerProps {
	text?: string;
	size?: "sm" | "md" | "lg";
	textColor?: string;
}

const LoadingSpinner = ({
	text = "Loading...",
	size = "md",
	textColor = "#000000",
}: LoadingSpinnerProps): JSX.Element => {
	const sizeClasses = {
		sm: "spinner-border-sm",
		md: "",
		lg: "spinner-border-lg",
	};

	return (
		<div className="d-flex flex-column justify-content-center align-items-center py-5">
			<div className={`spinner-border text-primary ${sizeClasses[size]}`} role="status">
				<span className="visually-hidden">{text}</span>
			</div>
			{text ? (
				<span className="mt-3" style={{ color: textColor }}>
					{text}
				</span>
			) : null}
		</div>
	);
};

export default LoadingSpinner;
