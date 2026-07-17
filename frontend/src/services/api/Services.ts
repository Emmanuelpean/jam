import {
	ForwardingConfirmationLinkData,
	JobEmailData,
	JobRatingData,
	JobRatingServiceLogData,
	JobScrapingServiceLogData,
	ScrapedJobData,
	ServiceError,
	ServiceLog,
} from "../schemas/Services";
import { ApiResponse, ApiResponsePromise, baseApi, QueryParams, serviceApi } from "./Base";
import { createCrudApi, CrudApi } from "./Crud";

// Scraped Job API
export interface ScrapedJobPlatformStat {
	platform: string;
	alert_name: string | null;
	scraped_count: number;
	imported_count: number;
	applied_count: number;
}

export interface ScrapedJobCrudApi extends CrudApi<ScrapedJobData> {
	getByFilterId: (filterId: number, token: string) => ApiResponsePromise<ScrapedJobData[]>;
	getByEmailId: (emailId: number, token: string) => ApiResponsePromise<ScrapedJobData[]>;
	platformStats: (token: string) => ApiResponsePromise<ScrapedJobPlatformStat[]>;
	getExpired: (token: string) => ApiResponsePromise<ScrapedJobData[]>;
	createTourDemo: (token: string) => ApiResponsePromise<ScrapedJobData>;
}

export const scrapedJobApi: ScrapedJobCrudApi = {
	...createCrudApi("scraped-jobs"),
	getByFilterId: (filterId: number, token: string): ApiResponsePromise<ScrapedJobData[]> =>
		baseApi.get(`scraped-jobs/filtered-by-filter/${filterId}`, token),
	getByEmailId: (emailId: number, token: string): ApiResponsePromise<ScrapedJobData[]> =>
		baseApi.get(`scraped-jobs/by-email/${emailId}`, token),
	platformStats: (token: string): ApiResponsePromise<ScrapedJobPlatformStat[]> =>
		baseApi.get("scraped-jobs/platform-stats", token),
	getExpired: (token: string): ApiResponsePromise<ScrapedJobData[]> => baseApi.get("scraped-jobs/expired", token),
	createTourDemo: (token: string): ApiResponsePromise<ScrapedJobData> =>
		baseApi.post("scraped-jobs/tour-demo", {}, token),
};

// Service Error API
export interface ServiceErrorCounts {
	job_email_scraping: number;
	job_rating: number;
	provider_monitoring: number;
}

export interface ServiceErrorApi {
	getAll: (token: string, queryParams?: QueryParams | null) => ApiResponsePromise<ServiceError[]>;
	acknowledge: (ids: number[], isAcknowledged: boolean, token: string) => ApiResponsePromise<ServiceError[]>;
	getUnacknowledgedCounts: (token: string) => ApiResponsePromise<ServiceErrorCounts>;
}

export const serviceErrorApi: ServiceErrorApi = {
	getAll: createCrudApi<ServiceError>("service-errors").getAll,
	acknowledge: (ids: number[], isAcknowledged: boolean, token: string): ApiResponsePromise<ServiceError[]> =>
		baseApi.put("service-errors/acknowledge", { ids, is_acknowledged: isAcknowledged }, token),
	getUnacknowledgedCounts: (token: string): ApiResponsePromise<ServiceErrorCounts> =>
		baseApi.get("service-errors/counts", token),
};

// Service Log APIs
export interface ServiceLogCrudApi<T = any> extends CrudApi {
	getLatest: (token: string) => ApiResponsePromise<T>;
}

const createServiceLogApi = <T>(serviceName: string): ServiceLogCrudApi<T> => ({
	...createCrudApi<T>(`service-logs/${serviceName}`),
	getLatest: (token: string): ApiResponsePromise<T> => baseApi.get(`service-logs/${serviceName}/latest`, token),
});

export const jobScraperServiceLogApi: ServiceLogCrudApi<JobScrapingServiceLogData> =
	createServiceLogApi<JobScrapingServiceLogData>("email_scraper_service");

export const jobRatingServiceLogApi: ServiceLogCrudApi<JobRatingServiceLogData> =
	createServiceLogApi<JobRatingServiceLogData>("job_rating_service");

export const providerMonitoringServiceLogApi: ServiceLogCrudApi<ServiceLog> =
	createServiceLogApi<ServiceLog>("provider_monitoring_service");

// Scheduled service APIs
export interface ServiceStatus {
	name: string;
	display_name: string;
	run_period_hours: number;
	parameters: Record<string, any>;
	is_enabled: boolean;
	is_running: boolean;
	last_run_at: string | null;
	next_run_at: string | null;
	last_log: string | null;
}

export interface ServiceUpdatePayload {
	is_enabled?: boolean;
	run_period_hours?: number;
	parameters?: Record<string, any>;
}

export interface LogResponse {
	lines: string[];
	total_lines: number;
}

export interface LogProvider {
	getLogs: (lines: number, token: string) => ApiResponsePromise<LogResponse>;
}

export interface BaseServiceApi extends LogProvider {
	getStatus: (token: string) => ApiResponsePromise<ServiceStatus | null>;
	update: (data: ServiceUpdatePayload, token: string) => ApiResponsePromise<ServiceStatus>;
	setEnabled: (enabled: boolean, token: string) => ApiResponsePromise<ServiceStatus>;
	runNow: (token: string) => ApiResponsePromise<ServiceStatus>;
}

export const createServiceApi = (serviceName: string): BaseServiceApi => ({
	getStatus: async (token: string): ApiResponsePromise<ServiceStatus | null> => {
		const res: ApiResponse<ServiceStatus[]> = await baseApi.get("services/", token);
		const match: ServiceStatus | null =
			res.data?.find((s: ServiceStatus): boolean => s.name === serviceName) ?? null;
		return { ...res, data: match };
	},
	update: (data: ServiceUpdatePayload, token: string): ApiResponsePromise<ServiceStatus> =>
		baseApi.patch(`services/${serviceName}`, data, token),
	setEnabled: (enabled: boolean, token: string): ApiResponsePromise<ServiceStatus> =>
		baseApi.patch(`services/${serviceName}`, { is_enabled: enabled }, token),
	runNow: (token: string): ApiResponsePromise<ServiceStatus> =>
		baseApi.post(`services/${serviceName}/run-now`, {}, token),
	getLogs: (lines: number, token: string): ApiResponsePromise<LogResponse> =>
		serviceApi.get(`services/${serviceName}/logs?lines=${lines}`, token),
});

export const jobScraperServiceApi: BaseServiceApi = createServiceApi("email_scraper_service");
export const jobRatingServiceRunnerApi: BaseServiceApi = createServiceApi("job_rating_service");

export interface SchedulerStatus {
	running: boolean;
	poll_interval_seconds: number;
	last_log: string | null;
}

export const schedulerApi: LogProvider & { getStatus: (token: string) => ApiResponsePromise<SchedulerStatus> } = {
	getStatus: (token: string): ApiResponsePromise<SchedulerStatus> =>
		serviceApi.get("service-scheduler/status", token),
	getLogs: (lines: number, token: string): ApiResponsePromise<LogResponse> =>
		serviceApi.get(`service-scheduler/logs?lines=${lines}`, token),
};

// Job Email API
export interface JobEmailCrudApi extends CrudApi<JobEmailData> {
	getByScrapedJobId: (jobId: number, token: string) => ApiResponsePromise<JobEmailData[]>;
}

export const jobEmailApi: JobEmailCrudApi = {
	...createCrudApi("job-alert-emails"),
	getByScrapedJobId: (jobId: number, token: string): ApiResponsePromise<JobEmailData[]> =>
		baseApi.get(`job-alert-emails/by-scraped-job/${jobId}`, token),
};

// Forwarding Confirmation Link API
export interface ForwardingConfirmationLinkApi {
	getPending: (token: string) => ApiResponsePromise<ForwardingConfirmationLinkData | null>;
	markAsUsed: (id: number, token: string) => ApiResponsePromise<ForwardingConfirmationLinkData>;
}

export const forwardingConfirmationApi: ForwardingConfirmationLinkApi = {
	getPending: (token: string): ApiResponsePromise<ForwardingConfirmationLinkData | null> =>
		baseApi.get("forwarding-confirmation-links/pending", token),
	markAsUsed: (id: number, token: string): ApiResponsePromise<ForwardingConfirmationLinkData> =>
		baseApi.put(`forwarding-confirmation-links/${id}`, { is_used: true }, token),
};
