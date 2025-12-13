import { useEffect, useState } from "react";
import { JobRatingServiceLog } from "../services/Schemas";
import { jobRatingServiceLogApi } from "../services/api/Services";
import { DateRange } from "../utils/TimeUtils";

export const useJobRatingServiceLogs = (token: string | null, isServiceRunning: boolean, dateRange: DateRange) => {
	const [serviceLogs, setServiceLogs] = useState<JobRatingServiceLog[] | null>(null);
	const [latestLog, setLatestLog] = useState<JobRatingServiceLog | null>(null);
	const [error, setError] = useState<string | null>(null);

	const fetchLatestLog = async (): Promise<void> => {
		if (!token) return;
		try {
			const log: JobRatingServiceLog = await jobRatingServiceLogApi.getLatest(token);
			if (log) {
				setLatestLog(log);
			}
		} catch (err: any) {
			setError(err.message || "An error occurred while fetching the latest log.");
			console.error("Failed to fetch latest log:", err);
		}
	};

	const fetchLatestLogs = async (): Promise<void> => {
		if (!token) return;
		try {
			const logs: JobRatingServiceLog[] = await jobRatingServiceLogApi.getAll(token, {
				start_date: new Date(dateRange.start).toISOString(),
				end_date: new Date(dateRange.end).toISOString(),
			});
			setServiceLogs(logs);
		} catch (err: any) {
			setError(err.message || "An error occurred while fetching the logs.");
			console.error("Failed to fetch latest logs:", err);
		}
	};

	useEffect((): void => {
		fetchLatestLogs().then();
	}, [token, dateRange]);

	// Fetch latest service log every 2s when scraper is running
	useEffect(() => {
		if (!isServiceRunning) return;
		fetchLatestLog().then();
		const interval = setInterval(fetchLatestLog, 2000);
		return (): void => clearInterval(interval);
	}, [isServiceRunning, token]);

	// Fetch the latest service log on component mount
	useEffect(() => {
		fetchLatestLog().then();
	}, [token]);

	return { serviceLogs, latestLog, fetchLatestLog, error };
};
