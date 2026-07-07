import { useEffect, useState } from "react";
import { BaseServiceApi, ServiceStatus } from "../services/api/Services";
import { useAuth } from "../contexts/AuthContext";

export const useServiceRunnerStatus = (api: BaseServiceApi) => {
	const { token } = useAuth();
	const [status, setStatus] = useState<ServiceStatus | null>(null);
	const [remainingTime, setRemainingTime] = useState<number | null>(null);
	const [statusError, setStatusError] = useState<string | null>(null);
	const [loading, setLoading] = useState<boolean>(true);

	const fetchStatus = async (): Promise<void> => {
		if (!token) return;
		try {
			const data = await api.getStatus(token);
			setStatus(data.data);
		} catch (err: any) {
			setStatusError(err.message || "Failed to fetch service status");
			console.error("An error occurred while fetching the service status", err);
		} finally {
			setLoading(false);
		}
	};

	// Fetch the scraper service status every 5 seconds
	useEffect(() => {
		fetchStatus().then();
		const interval = setInterval(fetchStatus, 5000);
		return (): void => clearInterval(interval);
	}, [token]);

	// Calculate and update the time remaining until the next scheduled run every second
	useEffect(() => {
		if (!status?.next_run_at) {
			setRemainingTime(null);
			return;
		}
		const updateTimer = (): void => {
			if (!status.next_run_at) return;
			const remaining: number = (new Date(status.next_run_at).getTime() - Date.now()) / 1000;
			setRemainingTime(remaining > 0 ? Math.round(remaining) : 0);
		};

		updateTimer();
		const interval = setInterval(updateTimer, 1000);
		return (): void => clearInterval(interval);
	}, [status?.next_run_at]);

	return { serviceStatus: status, remainingTime, fetchStatus, statusError, loading };
};
