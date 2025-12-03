import { useState, useEffect } from "react";
import { PlatformStat, ScrapedJobData, ServiceLog } from "../services/Schemas";
import { scrapedJobApi } from "../services/Api";

export const useScraperErrors = (
	latestLog: ServiceLog | ServiceLog[] | null,
	token: string | null,
	platform: string,
) => {
	const [scraperErrors, setScraperErrors] = useState<Record<string, number>>({});

	useEffect(() => {
		if (!latestLog || !token) return;

		const fetchErrors = async (): Promise<void> => {
			try {
				// Normalize input to array
				const logs: ServiceLog[] = Array.isArray(latestLog) ? latestLog : [latestLog];

				let ids: number[] = [];

				if (platform !== "all") {
					// Collect IDs from all logs for the specific platform
					logs.forEach((log: ServiceLog): void => {
						const platformStat: PlatformStat | undefined = log.platform_stats.find(
							(stat: PlatformStat): boolean => stat.name === platform,
						);
						if (platformStat?.job_scrape_failed_ids) {
							ids.push(...platformStat.job_scrape_failed_ids);
						}
					});
				} else {
					// Collect all IDs from all platforms across all logs
					logs.forEach((log: ServiceLog): void => {
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

				const scraped_jobs: ScrapedJobData[] = await scrapedJobApi.getBulk(ids, token);

				// Count errors
				const errorCounts: Record<string, number> = {};
				scraped_jobs.forEach((job: ScrapedJobData): void => {
					if (job.is_failed && job.scrape_error) {
						const errorMsg: string = job.scrape_error.trim();
						errorCounts[errorMsg] = (errorCounts[errorMsg] || 0) + 1;
					}
				});
				setScraperErrors(errorCounts);
			} catch (err: any) {
				console.error("Failed to fetch scraper errors:", err);
			}
		};

		fetchErrors().then();
	}, [latestLog, token, platform]);

	return { scraperErrors };
};
