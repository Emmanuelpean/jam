import { useState, useEffect } from "react";
import { PlatformStat, JobScraperServiceLog } from "../services/Schemas";
import { SelectOption } from "../components/rendering/form/FormOptions";
import { jobScraperServiceLogApi } from "../services/api/Services";
import { DateRange } from "../utils/TimeUtils";
import { capitalise } from "../utils/StringUtils";
import { useAuth } from "../contexts/AuthContext";

export const useJobScraperServiceLogs = (isScraperRunning: boolean, dateRange: DateRange) => {
	const { token } = useAuth();
	const [previousServiceLogs, setPreviousServiceLogs] = useState<JobScraperServiceLog[] | null>(null);
	const [latestServiceLog, setLatestServiceLog] = useState<JobScraperServiceLog | null>(null);
	const [platformOptions, setPlatformOptions] = useState<SelectOption[]>([]);
	const [serviceLogError, setServiceLogError] = useState<string | null>(null);

	const fetchLatestServiceLog = async (): Promise<void> => {
		if (!token) return;
		try {
			const log: JobScraperServiceLog = await jobScraperServiceLogApi.getLatest(token);
			if (log) {
				setLatestServiceLog(log);
			}
		} catch (err: any) {
			setServiceLogError(err.message || "An error occurred while fetching the latest log.");
			console.error("Failed to fetch latest log:", err);
		}
	};

	const fetchLatestLogs = async (): Promise<void> => {
		if (!token) return;
		try {
			const logs: JobScraperServiceLog[] = await jobScraperServiceLogApi.getAll(token, {
				start_date: new Date(dateRange.start).toISOString(),
				end_date: new Date(dateRange.end).toISOString(),
			});
			setPreviousServiceLogs(logs);

			// Extract unique platforms from logs
			const platformOptions: SelectOption[] = [
				{ value: "all", label: "All Platforms" },
				...Array.from(
					new Set(
						logs.flatMap((log: JobScraperServiceLog): string[] =>
							log.platform_stats ? log.platform_stats.map((stat: PlatformStat): string => stat.name) : [],
						),
					),
				).map(
					(platform: string): SelectOption => ({
						value: platform,
						label: capitalise(platform),
					}),
				),
			];
			setPlatformOptions(platformOptions);
		} catch (err: any) {
			setServiceLogError(err.message || "An error occurred while fetching the logs.");
			console.error("Failed to fetch latest logs:", err);
		}
	};

	useEffect(() => {
		fetchLatestLogs().then();
	}, [token, dateRange]);

	// Fetch latest service log every 2s when scraper is running
	useEffect(() => {
		if (!isScraperRunning) return;
		fetchLatestServiceLog().then();
		const interval = setInterval(fetchLatestServiceLog, 2000);
		return (): void => clearInterval(interval);
	}, [isScraperRunning, token]);

	// Fetch the latest service log on component mount
	useEffect(() => {
		fetchLatestServiceLog().then();
	}, [token]);

	return { previousServiceLogs, latestServiceLog, platformOptions, fetchLatestServiceLog, serviceLogError };
};
