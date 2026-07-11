import { useCallback, useEffect, useRef, useState } from "react";
import { ServiceError, ServiceLog } from "../services/schemas/Services";
import { serviceErrorApi } from "../services/api/Services";
import { useAuth } from "../contexts/AuthContext";
import { normaliseArray } from "../utils/Utils";
import { ApiResponse } from "../services/api/Base";

/** Which service-log foreign key on the unified Error table to filter by. */
export type ErrorFilterKey =
	| "job_email_scraping_service_log_id"
	| "job_rating_service_log_id"
	| "provider_monitoring_service_log_id";

export interface UseServiceErrorsResult {
	errors: ServiceError[];
	loading: boolean;
	requestError: Error | null;
	setAcknowledged: (ids: number[], isAcknowledged: boolean) => Promise<void>;
}

export interface ErrorGroup {
	errorType: string;
	message: string;
	ids: number[];
	count: number;
	isAcknowledged: boolean;
	jobs: { jobId: number; platform: string | null }[];
	errors: ServiceError[];
}

export const groupErrorsByMessage = (
	errors: ServiceError[],
	platformByJobId?: Record<number, string | null>
): ErrorGroup[] => {
	const groups = new Map<string, ErrorGroup>();
	errors.forEach((error: ServiceError): void => {
		const message: string = error.message.trim();
		const key: string = `${error.is_acknowledged ? 1 : 0}:${error.error_type}:${message}`;
		let group: ErrorGroup | undefined = groups.get(key);
		if (!group) {
			group = {
				errorType: error.error_type,
				message,
				ids: [],
				count: 0,
				isAcknowledged: error.is_acknowledged,
				jobs: [],
				errors: [],
			};
			groups.set(key, group);
		}
		group.ids.push(error.id);
		group.errors.push(error);
		group.count++;
		if (error.scraped_job_id != null) {
			group.jobs.push({ jobId: error.scraped_job_id, platform: platformByJobId?.[error.scraped_job_id] ?? null });
		}
	});
	return Array.from(groups.values()).sort((a: ErrorGroup, b: ErrorGroup): number => b.count - a.count);
};

export const useServiceErrors = (
	logs: ServiceLog | ServiceLog[] | null,
	filterKey: ErrorFilterKey,
	showAcknowledged: boolean,
	showLoadingOnUpdate: boolean = false
): UseServiceErrorsResult => {
	const { token } = useAuth();
	const [errors, setErrors] = useState<ServiceError[]>([]);
	const [loading, setLoading] = useState<boolean>(true);
	const [requestError, setRequestError] = useState<Error | null>(null);
	const hasLoaded = useRef<boolean>(false);

	const logIds: number[] = logs ? normaliseArray(logs).map((log: ServiceLog): number => log.id) : [];
	const logIdsKey: string = logIds.join(",");

	const fetchErrors = useCallback(async (): Promise<void> => {
		if (!token || logIds.length === 0) {
			setErrors([]);
			setLoading(false);
			return;
		}
		if (!hasLoaded.current || showLoadingOnUpdate) {
			setLoading(true);
		}
		try {
			const params: Record<string, any> = { [filterKey]: logIds, is_acknowledged: showAcknowledged };
			const response: ApiResponse<ServiceError[]> = await serviceErrorApi.getAll(token, params);
			setErrors(response.data);
			setRequestError(null);
			hasLoaded.current = true;
		} catch (err: any) {
			setRequestError(err || new Error("Failed to fetch service errors"));
			console.error("Failed to fetch service errors:", err);
		} finally {
			setLoading(false);
		}
	}, [token, logIdsKey, filterKey, showAcknowledged]);

	useEffect((): void => {
		fetchErrors().then();
	}, [fetchErrors]);

	const setAcknowledged = useCallback(
		async (ids: number[], isAcknowledged: boolean): Promise<void> => {
			if (!token || ids.length === 0) return;
			const affected: Set<number> = new Set(ids);
			await serviceErrorApi.acknowledge(ids, isAcknowledged, token);
			setErrors((current: ServiceError[]): ServiceError[] => {
				const updated: ServiceError[] = current.map(
					(error: ServiceError): ServiceError =>
						affected.has(error.id) ? { ...error, is_acknowledged: isAcknowledged } : error
				);
				return updated.filter((error: ServiceError): boolean => error.is_acknowledged === showAcknowledged);
			});
		},
		[token, showAcknowledged]
	);

	return { errors, loading, requestError, setAcknowledged };
};
