import { useEffect, useRef, useState } from "react";
import { JobScrapingServiceLogData, ServiceError } from "../services/schemas/Services";
import { normaliseArray } from "../utils/Utils";

export const useServiceErrors = (
	latestLog: JobScrapingServiceLogData | JobScrapingServiceLogData[] | null,
	showLoadingOnUpdate: boolean = false
) => {
	const [serviceErrors, setServiceErrors] = useState<Record<string, number>>({});
	const [loading, setLoading] = useState<boolean>(true);
	const hasLoaded = useRef<boolean>(false);

	useEffect(() => {
		if (!latestLog) return;

		const fetchErrors = async (): Promise<void> => {
			if (!hasLoaded.current || showLoadingOnUpdate) {
				setLoading(true);
			}
			try {
				const logs: JobScrapingServiceLogData[] = normaliseArray(latestLog);
				const allErrors: ServiceError[] = logs.flatMap(
					(log: JobScrapingServiceLogData): ServiceError[] => log.service_errors
				);

				// Count errors by message
				const errorCounts: Record<string, number> = {};
				allErrors.forEach((error: ServiceError): void => {
					const errorMsg: string = error.message.trim();
					errorCounts[errorMsg] = (errorCounts[errorMsg] || 0) + 1;
				});

				setServiceErrors(errorCounts);
				hasLoaded.current = true;
			} catch (err: any) {
				console.error("Failed to fetch service errors:", err);
			} finally {
				setLoading(false);
			}
		};

		fetchErrors().then();
	}, [latestLog]);

	return { serviceErrors, loading };
};
