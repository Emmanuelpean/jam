import { useEffect, useState } from "react";
import { JobRatingData, JobRatingServiceLogData } from "../services/Schemas";
import { jobRatingApi } from "../services/api/Services";
import { normaliseArray } from "../utils/Utils";
import { useAuth } from "../contexts/AuthContext";

export const useJobRatingErrors = (latestLog: JobRatingServiceLogData | JobRatingServiceLogData[] | null) => {
	const { token } = useAuth();
	const [scraperErrors, setScraperErrors] = useState<Record<string, number>>({});
	const [error, setError] = useState<Error | null>(null);

	useEffect((): void => {
		if (!latestLog || !token) return;

		const fetchErrors = async (): Promise<void> => {
			try {
				// Get the job rating failed IDs from the logs
				const logs: JobRatingServiceLogData[] = normaliseArray(latestLog);
				let ids: number[] = logs.flatMap((log: JobRatingServiceLogData): number[] => log.rated_job_failed_ids);
				ids = [...new Set(ids)];

				// Get the job rating data for the failed IDs
				const jobRatings: JobRatingData[] = await jobRatingApi.getAll(token, { id: ids });
				const errorCounts: Record<string, number> = {};
				jobRatings.forEach((job: JobRatingData): void => {
					if (!job.is_success && job.error) {
						const errorMsg: string = job.error.trim();
						errorCounts[errorMsg] = (errorCounts[errorMsg] || 0) + 1;
					}
				});
				setScraperErrors(errorCounts);
			} catch (err: any) {
				setError(err || new Error("Failed to fetch errors"));
				console.error("Failed to fetch errors:", err);
			}
		};

		fetchErrors().then();
	}, [latestLog, token]);

	return { scraperErrors, error };
};
