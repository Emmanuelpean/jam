import React, { JSX } from "react";
import { ServiceStatus } from "../../../services/api/Services";

interface LastLogBarProps {
	serviceStatus: ServiceStatus | null;
	/** Clicking (or keyboard-activating) the bar — typically opens the log viewer. */
	onClick: () => void;
	className?: string;
}

/**
 * Compact bar showing the most recent log line while a service run is in progress. Clicking it
 * is wired by the parent to open and scroll to the full log viewer.
 */
export const LastLogBar = ({ serviceStatus, onClick, className }: LastLogBarProps): JSX.Element | null => {
	if (!serviceStatus?.is_running || !serviceStatus.last_log) return null;

	return (
		<div
			className={`service-last-log${className ? ` ${className}` : ""}`}
			role="button"
			tabIndex={0}
			onClick={onClick}
			onKeyDown={(e: React.KeyboardEvent): void => {
				if (e.key === "Enter" || e.key === " ") {
					e.preventDefault();
					onClick();
				}
			}}
		>
			<span className="live-indicator" />
			<span className="service-last-log-text">{serviceStatus.last_log}</span>
		</div>
	);
};
