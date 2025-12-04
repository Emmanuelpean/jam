import { useState, useEffect } from "react";
import { jobScraperServiceApi, ScraperStatus } from "../services/Api";

export const useScraperStatus = (token: string | null) => {
	const [status, setStatus] = useState<ScraperStatus | null>(null);
	const [remainingTime, setRemainingTime] = useState<number | null>(null);

	const fetchStatus = async (): Promise<void> => {
		if (!token) return;
		try {
			const data: ScraperStatus = await jobScraperServiceApi.getStatus(token);
			setStatus(data);
		} catch (err: any) {
			console.error("An error occured while fetching the service status", err);
		}
	};

	// Fetch the scraper service status every 5 seconds
	useEffect(() => {
		fetchStatus().then();
		const interval = setInterval(fetchStatus, 5000);
		return (): void => clearInterval(interval);
	}, [token]);

	// Calculate and update remaining time every second
	useEffect(() => {
		if (!status?.sleep_until) {
			setRemainingTime(null);
			return;
		}
		const updateTimer = (): void => {
			if (!status.sleep_until) return;
			const remaining: number = new Date(status.sleep_until).getTime() - Date.now() / 1000;
			setRemainingTime(remaining > 0 ? Math.round(remaining) : 0);
		};

		updateTimer();
		const interval = setInterval(updateTimer, 1000);
		return (): void => clearInterval(interval);
	}, [status?.sleep_until]);

	return { status, remainingTime, fetchStatus };
};
