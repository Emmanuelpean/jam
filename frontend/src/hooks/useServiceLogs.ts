import { useEffect, useRef, useState } from "react";
import { DateRange } from "../utils/TimeUtils";
import { useAuth } from "../contexts/AuthContext";
import { ApiResponse } from "../services/api/Base";

interface ServiceLogApi<T> {
	getLatest: (token: string) => Promise<ApiResponse<T>>;
	getAll: (token: string, params: Record<string, any>) => Promise<ApiResponse<T[]>>;
}

export const useServiceLogs = <T>(
	logApi: ServiceLogApi<T>,
	isServiceRunning: boolean,
	dateRange: DateRange | null,
	onLogsLoaded?: (logs: T[]) => void
) => {
	const { token } = useAuth();
	const [previousServiceLogs, setPreviousServiceLogs] = useState<T[] | null>(null);
	const [latestServiceLog, setLatestServiceLog] = useState<T | null>(null);
	const [serviceLogError, setServiceLogError] = useState<string | null>(null);
	const [loading, setLoading] = useState<boolean>(true);
	const fetchSeqRef = useRef<number>(0);

	const fetchLatestServiceLog = async (): Promise<void> => {
		if (!token) return;
		try {
			const log: ApiResponse<T> = await logApi.getLatest(token);
			if (log.data) setLatestServiceLog(log.data);
		} catch (err: any) {
			setServiceLogError(err.message || "An error occurred while fetching the latest log.");
			console.error("Failed to fetch latest log:", err);
		}
	};

	const fetchLatestLogs = async (): Promise<void> => {
		if (!token || !dateRange) return;
		const seq = ++fetchSeqRef.current;
		setLoading(true);
		try {
			const logs: ApiResponse<T[]> = await logApi.getAll(token, {
				start_date: new Date(dateRange.start).toISOString(),
				end_date: new Date(dateRange.end).toISOString(),
			});
			if (seq !== fetchSeqRef.current) return;
			setPreviousServiceLogs(logs.data);
			onLogsLoaded?.(logs.data);
		} catch (err: any) {
			if (seq !== fetchSeqRef.current) return;
			setServiceLogError(err.message || "An error occurred while fetching the logs.");
			console.error("Failed to fetch latest logs:", err);
		} finally {
			if (seq === fetchSeqRef.current) setLoading(false);
		}
	};

	useEffect((): void => {
		fetchLatestLogs().then();
	}, [token, dateRange]);

	useEffect(() => {
		if (!isServiceRunning) return;
		fetchLatestServiceLog().then();
		const interval = setInterval(fetchLatestServiceLog, 2000);
		return (): void => clearInterval(interval);
	}, [isServiceRunning, token]);

	useEffect(() => {
		fetchLatestServiceLog().then();
	}, [token]);

	return { previousServiceLogs, latestServiceLog, fetchLatestServiceLog, serviceLogError, loading };
};
