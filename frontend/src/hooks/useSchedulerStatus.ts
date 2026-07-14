import { useEffect, useState } from "react";
import { schedulerApi, SchedulerStatus } from "../services/api/Services";
import { useAuth } from "../contexts/AuthContext";

export const useSchedulerStatus = () => {
	const { token } = useAuth();
	const [status, setStatus] = useState<SchedulerStatus | null>(null);
	const [statusError, setStatusError] = useState<string | null>(null);
	const [loading, setLoading] = useState<boolean>(true);

	const fetchStatus = async (): Promise<void> => {
		if (!token) return;
		try {
			const data = await schedulerApi.getStatus(token);
			setStatus(data.data);
		} catch (err: any) {
			setStatusError(err.message || "Failed to fetch scheduler status");
			console.error("An error occurred while fetching the scheduler status", err);
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		fetchStatus().then();
		const interval = setInterval(fetchStatus, 5000);
		return (): void => clearInterval(interval);
	}, [token]);

	return { schedulerStatus: status, fetchStatus, statusError, loading };
};
