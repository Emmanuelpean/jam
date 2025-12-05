import { useEffect, useState } from "react";
import { ServiceError, ServiceLog } from "../services/Schemas";
import { normaliseArray } from "../utils/Utils";

export const useServiceErrors = (latestLog: ServiceLog | ServiceLog[] | null, token: string | null) => {
	const [serviceErrors, setServiceErrors] = useState<Record<string, number>>({});

	useEffect(() => {
		if (!latestLog || !token) return;

		const fetchErrors = async (): Promise<void> => {
			try {
				const logs: ServiceLog[] = normaliseArray(latestLog);
				const allErrors: ServiceError[] = logs.flatMap((log: ServiceLog): ServiceError[] => log.service_errors);

				// Count errors by message
				const errorCounts: Record<string, number> = {};
				allErrors.forEach((error: ServiceError): void => {
					const errorMsg: string = error.message.trim();
					errorCounts[errorMsg] = (errorCounts[errorMsg] || 0) + 1;
				});

				setServiceErrors(errorCounts);
			} catch (err: any) {
				console.error("Failed to fetch service errors:", err);
			}
		};

		fetchErrors().then();
	}, [latestLog, token]);

	return { serviceErrors };
};
