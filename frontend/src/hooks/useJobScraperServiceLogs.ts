import { useState } from "react";
import { JobScrapingServiceLogData, PlatformStat } from "../services/schemas/Services";
import { SelectOption } from "../components/rendering/form/FormOptions";
import { jobScraperServiceLogApi } from "../services/api/Services";
import { DateRange } from "../utils/TimeUtils";
import { capitalise } from "../utils/StringUtils";
import { useServiceLogs } from "./useServiceLogs";

export const useJobScraperServiceLogs = (isScraperRunning: boolean, dateRange: DateRange | null) => {
	const [platformOptions, setPlatformOptions] = useState<SelectOption[]>([]);

	const result = useServiceLogs<JobScrapingServiceLogData>(
		jobScraperServiceLogApi,
		isScraperRunning,
		dateRange,
		(logs: JobScrapingServiceLogData[]) => {
			setPlatformOptions([
				{ value: "all", label: "All Platforms" },
				...Array.from(
					new Set(
						logs.flatMap((log) =>
							log.platform_stats ? log.platform_stats.map((stat: PlatformStat) => stat.name) : []
						)
					)
				).map((platform: string): SelectOption => ({ value: platform, label: capitalise(platform) })),
			]);
		}
	);

	return { ...result, platformOptions };
};
