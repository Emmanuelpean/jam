import { useState, useEffect } from "react";
import { PlatformStat, ServiceLog } from "../services/Schemas";
import { SelectOption } from "../components/rendering/form/FormOptions";
import { serviceLogApi } from "../services/Api";
import { capitalise } from "../utils/Utils";

export const useServiceLogs = (token: string | null, isScraperRunning: boolean) => {
	const [serviceLogs, setServiceLogs] = useState<ServiceLog[] | null>(null);
	const [latestLog, setLatestLog] = useState<ServiceLog | null>(null);
	const [platformOptions, setPlatformOptions] = useState<SelectOption[]>([]);

	const fetchLatestLog = async (): Promise<void> => {
		if (!token) return;
		try {
			const log: ServiceLog = await serviceLogApi.getLatest(token);
			if (log) {
				setLatestLog(log);
			}
		} catch (err: any) {
			console.error("Failed to fetch latest log:", err);
		}
	};

	const fetchLatestLogs = async (): Promise<void> => {
		if (!token) return;
		try {
			const logs: ServiceLog[] = await serviceLogApi.getAll(token, { limit: 10 });
			setServiceLogs(logs);

			// Extract unique platforms from logs
			const platformOptions: SelectOption[] = [
				{ value: "all", label: "All Platforms" },
				...Array.from(
					new Set(
						logs.flatMap((log: ServiceLog): string[] =>
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
			console.error("Failed to fetch latest logs:", err);
		}
	};

	useEffect(() => {
		fetchLatestLogs().then();
	}, [token]);

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

	return { serviceLogs, latestLog, platformOptions, fetchLatestLog };
};
