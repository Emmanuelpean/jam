import { useCallback, useEffect, useRef, useState } from "react";
import { ServiceError, ServiceLog } from "../services/schemas/Services";
import { serviceErrorApi } from "../services/api/Services";
import { useAuth } from "../contexts/AuthContext";
import { normaliseArray } from "../utils/Utils";

/** Which service-log foreign key on the unified Error table to filter by. */
export type ErrorFilterKey =
	| "job_email_scraping_service_log_id"
	| "job_rating_service_log_id"
	| "provider_monitoring_service_log_id";

export interface UseServiceErrorsResult {
	errors: ServiceError[];
	loading: boolean;
	requestError: Error | null;
	/** Acknowledge the given errors then refresh (acknowledged errors drop out unless shown). */
	acknowledge: (ids: number[]) => Promise<void>;
}

/** A set of errors sharing the same message, with the ids needed to acknowledge them. */
export interface ErrorGroup {
	message: string;
	ids: number[];
	count: number;
	jobs: { jobId: number; platform: string | null }[];
}

/** Group errors by message (descending by occurrence), attaching per-job context when present. */
export const groupErrorsByMessage = (
	errors: ServiceError[],
	platformByJobId?: Record<number, string | null>
): ErrorGroup[] => {
	const groups = new Map<string, ErrorGroup>();
	errors.forEach((error: ServiceError): void => {
		const key: string = error.message.trim();
		let group: ErrorGroup | undefined = groups.get(key);
		if (!group) {
			group = { message: key, ids: [], count: 0, jobs: [] };
			groups.set(key, group);
		}
		group.ids.push(error.id);
		group.count++;
		if (error.scraped_job_id != null) {
			group.jobs.push({ jobId: error.scraped_job_id, platform: platformByJobId?.[error.scraped_job_id] ?? null });
		}
	});
	return Array.from(groups.values()).sort((a, b) => b.count - a.count);
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
			const params: Record<string, any> = { [filterKey]: logIds };
			if (!showAcknowledged) {
				params.is_acknowledged = false;
			}
			const response = await serviceErrorApi.getAll(token, params);
			setErrors(response.data);
			setRequestError(null);
			hasLoaded.current = true;
		} catch (err: any) {
			setRequestError(err || new Error("Failed to fetch service errors"));
			console.error("Failed to fetch service errors:", err);
		} finally {
			setLoading(false);
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [token, logIdsKey, filterKey, showAcknowledged]);

	useEffect((): void => {
		fetchErrors().then();
	}, [fetchErrors]);

	const acknowledge = useCallback(
		async (ids: number[]): Promise<void> => {
			if (!token || ids.length === 0) return;
			await serviceErrorApi.acknowledge(ids, true, token);
			await fetchErrors();
		},
		[token, fetchErrors]
	);

	return { errors, loading, requestError, acknowledge };
};
