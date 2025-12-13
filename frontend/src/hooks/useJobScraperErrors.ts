import { useState, useEffect } from "react";
import { PlatformStat, ScrapedJobData, JobScraperServiceLog } from "../services/Schemas";
import { scrapedJobApi } from "../services/api/Services";
import { normaliseArray } from "../utils/Utils";

export const useJobScraperErrors = (
	latestLog: JobScraperServiceLog | JobScraperServiceLog[] | null,
	token: string | null,
	platform: string,
) => {
	const [scraperErrors, setScraperErrors] = useState<Record<string, number>>({});

	useEffect(() => {
		if (!latestLog || !token) return;

		const fetchErrors = async (): Promise<void> => {
			try {
				// Normalize input to array
				const logs: JobScraperServiceLog[] = normaliseArray(latestLog);

				let ids: number[] = [];

				if (platform !== "all") {
					// Collect IDs from all logs for the specific platform
					logs.forEach((log: JobScraperServiceLog): void => {
						const platformStat: PlatformStat | undefined = log.platform_stats.find(
							(stat: PlatformStat): boolean => stat.name === platform,
						);
						if (platformStat?.job_scrape_failed_ids) {
							ids.push(...platformStat.job_scrape_failed_ids);
						}
					});
				} else {
					// Collect all IDs from all platforms across all logs
					logs.forEach((log: JobScraperServiceLog): void => {
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

				const scraped_jobs: ScrapedJobData[] = await scrapedJobApi.getAll(token, { id: ids });

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
