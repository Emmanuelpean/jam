import { useState, useEffect } from "react";
import { PlatformStat, JobScraperServiceLog } from "../services/Schemas";
import { SelectOption } from "../components/rendering/form/FormOptions";
import { jobScraperServiceLogApi } from "../services/api/Services";
import { DateRange } from "../utils/TimeUtils";
import { capitalise } from "../utils/StringUtils";

export const useJobScraperServiceLogs = (token: string | null, isScraperRunning: boolean, dateRange: DateRange) => {
	const [serviceLogs, setServiceLogs] = useState<JobScraperServiceLog[] | null>(null);
	const [latestLog, setLatestLog] = useState<JobScraperServiceLog | null>(null);
	const [platformOptions, setPlatformOptions] = useState<SelectOption[]>([]);
	const [error, setError] = useState<string | null>(null);

	const fetchLatestLog = async (): Promise<void> => {
		if (!token) return;
		try {
			const log: JobScraperServiceLog = await jobScraperServiceLogApi.getLatest(token);
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
			const logs: JobScraperServiceLog[] = await jobScraperServiceLogApi.getAll(token, {
				start_date: new Date(dateRange.start).toISOString(),
				end_date: new Date(dateRange.end).toISOString(),
			});
			setServiceLogs(logs);

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
			setError(err.message || "An error occurred while fetching the logs.");
			console.error("Failed to fetch latest logs:", err);
		}
	};

	useEffect(() => {
		fetchLatestLogs().then();
	}, [token, dateRange]);

	// Fetch latest service log every 2s when scraper is running
	useEffect(() => {
		if (!isScraperRunning) return;
		fetchLatestLog().then();
		const interval = setInterval(fetchLatestLog, 2000);
		return (): void => clearInterval(interval);
	}, [isScraperRunning, token]);

	// Fetch the latest service log on component mount
	useEffect(() => {
		fetchLatestLog().then();
	}, [token]);

	return { serviceLogs, latestLog, platformOptions, fetchLatestLog, error };
};
