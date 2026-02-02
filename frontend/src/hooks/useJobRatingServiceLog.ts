import { useEffect, useState } from "react";
import { JobRatingServiceLogData } from "../services/schemas/Services";
import { jobRatingServiceLogApi } from "../services/api/Services";
import { DateRange } from "../utils/TimeUtils";
import { useAuth } from "../contexts/AuthContext";
import { ApiResponse } from "../services/api/Base";

export const useJobRatingServiceLogs = (isServiceRunning: boolean, dateRange: DateRange) => {
	const { token } = useAuth();
	const [previousServiceLogs, setPreviousServiceLogs] = useState<JobRatingServiceLogData[] | null>(null);
	const [latestServiceLog, setLatestServiceLog] = useState<JobRatingServiceLogData | null>(null);
	const [serviceLogError, setServiceLogError] = useState<string | null>(null);
	const [loading, setLoading] = useState<boolean>(true);

	const fetchLatestServiceLog = async (): Promise<void> => {
		if (!token) return;
		try {
			const log: ApiResponse<JobRatingServiceLogData> = await jobRatingServiceLogApi.getLatest(token);
			if (log.data) {
				setLatestServiceLog(log.data);
			}
		} catch (err: any) {
			setServiceLogError(err.message || "An error occurred while fetching the latest log.");
			console.error("Failed to fetch latest log:", err);
		}
	};

	const fetchLatestLogs = async (): Promise<void> => {
		if (!token) return;
		setLoading(true);
		try {
			const logs: ApiResponse<JobRatingServiceLogData[]> = await jobRatingServiceLogApi.getAll(token, {
				start_date: new Date(dateRange.start).toISOString(),
				end_date: new Date(dateRange.end).toISOString(),
			});
			setPreviousServiceLogs(logs.data);
		} catch (err: any) {
			setServiceLogError(err.message || "An error occurred while fetching the logs.");
			console.error("Failed to fetch latest logs:", err);
		} finally {
			setLoading(false);
		}
	};

	useEffect((): void => {
		fetchLatestLogs().then();
	}, [token, dateRange]);

	// Fetch latest service log every 2s when scraper is running
	useEffect(() => {
		if (!isServiceRunning) return;
		fetchLatestServiceLog().then();
		const interval = setInterval(fetchLatestServiceLog, 2000);
		return (): void => clearInterval(interval);
	}, [isServiceRunning, token]);

	// Fetch the latest service log on component mount
	useEffect(() => {
		fetchLatestServiceLog().then();
	}, [token]);

	return { previousServiceLogs, latestServiceLog, fetchLatestServiceLog, serviceLogError, loading };
};
