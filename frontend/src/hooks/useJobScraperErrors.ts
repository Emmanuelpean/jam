import { useState, useEffect } from "react";
import { PlatformStat, ScrapedJobData, JobScrapingServiceLogData } from "../services/schemas/Services";
import { scrapedJobApi } from "../services/api/Services";
import { normaliseArray } from "../utils/Utils";
import { useAuth } from "../contexts/AuthContext";
import { ApiResponse } from "../services/api/Base";

export interface ErrorCount {
	count: number;
	jobs: Array<{ jobId: number; platform: string | null }>;
}

export const useJobScraperErrors = (
	latestLog: JobScrapingServiceLogData | JobScrapingServiceLogData[] | null,
	platform: string,
) => {
	const { token } = useAuth();
	const [scraperErrors, setScraperErrors] = useState<Record<string, ErrorCount>>({});
	const [error, setError] = useState<Error | null>(null);

	useEffect(() => {
		if (!latestLog || !token) return;

		const fetchErrors = async (): Promise<void> => {
			try {
				// Normalize input to array
				const logs: JobScrapingServiceLogData[] = normaliseArray(latestLog);

				let ids: number[] = [];

				if (platform !== "all") {
					// Collect IDs from all logs for the specific platform
					logs.forEach((log: JobScrapingServiceLogData): void => {
						const platformStat: PlatformStat | undefined = log.platform_stats.find(
							(stat: PlatformStat): boolean => stat.name === platform,
						);
						if (platformStat?.job_scrape_failed_ids) {
							ids.push(...platformStat.job_scrape_failed_ids);
						}
					});
				} else {
					// Collect all IDs from all platforms across all logs
					logs.forEach((log: JobScrapingServiceLogData): void => {
						log.platform_stats.forEach((stat: PlatformStat): void => {
							if (stat.job_scrape_failed_ids) {
								ids.push(...stat.job_scrape_failed_ids);
							}
						});
					});
				}

				// Remove duplicates
				ids = [...new Set(ids)];

				if (!ids.length) {
					setScraperErrors({});
					return;
				}

				const scraped_jobs: ApiResponse<ScrapedJobData[]> = await scrapedJobApi.getAll(token, { id: ids });

				const errorCounts: Record<string, ErrorCount> = {};
				scraped_jobs.data.forEach((job: ScrapedJobData): void => {
					if (job.is_failed && job.scrape_error) {
						const errorMsg: string = job.scrape_error.trim();
						if (!errorCounts[errorMsg]) {
							errorCounts[errorMsg] = { count: 0, jobs: [] };
						}
						errorCounts[errorMsg].count++;
						errorCounts[errorMsg].jobs.push({
							jobId: job.id,
							platform: job.platform,
						});
					}
				});
				setScraperErrors(errorCounts);
			} catch (err: any) {
				setError(err || new Error("Failed to fetch scraper errors"));
				console.error("Failed to fetch scraper errors:", err);
			}
		};

		fetchErrors().then();
	}, [latestLog, token, platform]);

	return { scraperErrors, error };
};
