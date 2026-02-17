import React, { JSX, useEffect, useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useStatus } from "../../contexts/StatusContext";
import { AppBanner } from "./AppBanner";
import { formatDuration, formatScheduledTime, ONE_HOUR_IN_SECONDS } from "../../utils/TimeUtils";

export function MaintenanceBanner(): JSX.Element | null {
	const { currentUser } = useAuth();
	const { maintenanceMode, maintenanceScheduledAt } = useStatus();
	const [secondsLeft, setSecondsLeft] = useState<number | null>(null);
	const [bannerDismissed, setBannerDismissed] = useState(false);

	// Live countdown for a scheduled pre-maintenance window.
	// Only runs when the scheduled time is in the future and the user is authenticated.
	useEffect(() => {
		if (!maintenanceScheduledAt || maintenanceMode) {
			setSecondsLeft(null);
			return;
		}

		const scheduledTime: number = new Date(maintenanceScheduledAt).getTime();

		if (isNaN(scheduledTime)) {
			setSecondsLeft(null);
			return;
		}

		const initialDiff: number = Math.ceil((scheduledTime - Date.now()) / 1000);

		if (initialDiff <= 0) {
			setSecondsLeft(null);
			return;
		}

		setSecondsLeft(initialDiff);

		const interval = setInterval(() => {
			const remaining: number = Math.ceil((scheduledTime - Date.now()) / 1000);

			if (remaining <= 0) {
				setSecondsLeft(null);
				clearInterval(interval);
				return;
			}

			setSecondsLeft(remaining);
		}, 1000);

		return () => clearInterval(interval);
	}, [maintenanceScheduledAt, maintenanceMode]);

	const showUpcomingBanner = secondsLeft !== null && secondsLeft > 0 && !bannerDismissed;
	const showAdminMaintenanceBanner: boolean = maintenanceMode && !!currentUser?.is_admin;
	const showMaintenanceActiveBanner: boolean = maintenanceMode && !currentUser?.is_admin;

	if (!showUpcomingBanner && !showAdminMaintenanceBanner && !showMaintenanceActiveBanner) return null;

	return (
		<>
			{showUpcomingBanner && (
				<AppBanner
					icon="bi-clock-history"
					colorClass="bg-warning"
					id="maintenance-countdown-banner"
					role="alert"
					onDismiss={() => setBannerDismissed(true)}
					dismissLabel="Dismiss maintenance notice"
				>
					{secondsLeft > ONE_HOUR_IN_SECONDS ? (
						<>
							Scheduled maintenance on{" "}
							<strong>{formatScheduledTime(new Date(maintenanceScheduledAt!))}</strong>. The app will be
							temporarily unavailable.
						</>
					) : (
						<>
							Maintenance in <strong>{formatDuration(secondsLeft)}</strong>. The app will go offline for
							updates.
						</>
					)}
				</AppBanner>
			)}

			{showMaintenanceActiveBanner && (
				<AppBanner
					icon="bi-exclamation-triangle-fill"
					colorClass="bg-danger"
					id="maintenance-error-banner"
					role="alert"
				>
					<strong>App is being updated.</strong> JAM is currently undergoing maintenance. The application will
					be back shortly. Any unsaved changes will not be saved.
				</AppBanner>
			)}
			{showAdminMaintenanceBanner && (
				<AppBanner
					icon="bi-exclamation-triangle-fill"
					colorClass="bg-danger"
					id="maintenance-error-banner"
					role="alert"
				>
					<strong>Maintenance mode is active.</strong> Regular users are blocked from the API. Toggle it off
					via <strong>App Settings</strong>.
				</AppBanner>
			)}
		</>
	);
}
