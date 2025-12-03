import { useState, useEffect } from "react";
import { ServiceLog, ServiceError } from "../services/Schemas";
import { serviceErrorApi } from "../services/Api";

export const useServiceErrors = (latestLog: ServiceLog | ServiceLog[] | null, token: string | null) => {
	const [serviceErrors, setServiceErrors] = useState<Record<string, number>>({});

	useEffect(() => {
		if (!latestLog || !token) return;

		const fetchErrors = async (): Promise<void> => {
			try {
				// Normalize input to array
				const logs: ServiceLog[] = Array.isArray(latestLog) ? latestLog : [latestLog];

				// Collect all service log IDs
				const logIds: number[] = logs.map((log: ServiceLog): number => log.id);

				// Fetch all service errors for these log IDs
				const allErrors: ServiceError[] = await serviceErrorApi.getAll(token, {
					service_log_ids: logIds,
				});

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
