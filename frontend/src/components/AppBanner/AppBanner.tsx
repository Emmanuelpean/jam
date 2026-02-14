import React, { JSX } from "react";
import "./AppBanner.scss";

interface AppBannerProps {
	icon: string;
	colorClass: string;
	id: string;
	role?: "status" | "alert";
	onDismiss?: () => void;
	dismissLabel?: string;
	children: React.ReactNode;
}

export function AppBanner({
	icon,
	colorClass,
	id,
	role = "status",
	onDismiss,
	dismissLabel = "Dismiss",
	children,
}: AppBannerProps): JSX.Element {
	return (
		<div className={`app-banner ${colorClass}${onDismiss ? " has-dismiss" : ""}`} role={role} id={id}>
			<div className="app-banner-content">
				<i className={`bi ${icon}`} />
				<span>{children}</span>
			</div>
			{onDismiss && (
				<button
					type="button"
					className="app-banner-dismiss-btn"
					onClick={onDismiss}
					aria-label={dismissLabel}
				>
					<i className="bi bi-x-lg" />
				</button>
			)}
		</div>
	);
}