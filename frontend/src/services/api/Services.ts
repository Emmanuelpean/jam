import {
	AiSystemPromptData,
	JobRatingData,
	JobRatingServiceLogData,
	JobScrapingServiceLogData,
	ScrapedJobData,
} from "../schemas/Services";
import { ApiResponsePromise, baseApi, serviceApi } from "./Base";
import { createCrudApi, CrudApi } from "./Crud";

// Scraped Job API
export interface ScrapedJobCrudApi extends CrudApi<ScrapedJobData> {
	getCount: (token: string) => ApiResponsePromise<{ count: number }>;
	getByFilterId: (filterId: number, token: string) => ApiResponsePromise<ScrapedJobData[]>;
}

export const scrapedJobApi: ScrapedJobCrudApi = {
	...createCrudApi("scraped-jobs"),
	getCount: (token: string): ApiResponsePromise<{ count: number }> => baseApi.get("scraped-jobs/count", token),
	getByFilterId: (filterId: number, token: string): ApiResponsePromise<ScrapedJobData[]> =>
		baseApi.get(`scraped-jobs/filtered-by-filter/${filterId}`, token),
};

// Job Rating APIs
export const jobRatingApi: CrudApi<JobRatingData> = createCrudApi("job-ratings");

// Service Log APIs
export interface ServiceLogCrudApi<T = any> extends CrudApi {
	getLatest: (token: string) => ApiResponsePromise<T>;
}

export const jobScraperServiceLogApi: ServiceLogCrudApi<JobScrapingServiceLogData> = {
	...createCrudApi("job-scraping-service-logs"),
	getLatest: (token: string): ApiResponsePromise<JobScrapingServiceLogData> =>
		baseApi.get("job-scraping-service-logs/latest", token),
};

export const jobRatingServiceLogApi: ServiceLogCrudApi<JobRatingServiceLogData> = {
	...createCrudApi("job-rating-service-logs"),
	getLatest: (token: string): ApiResponsePromise<JobRatingServiceLogData> =>
		baseApi.get("job-rating-service-logs/latest", token),
};

// Service Runner APIs
export type ThreadStatus = "started" | "stopped" | "starting" | "stopping";

export interface ServiceStatus {
	service_runner_status: ThreadStatus;
	service_running: boolean;
	service_kwargs: any;
	period_hours: number | null;
	sleep_until: Date | null;
	last_log: string | null;
}

interface ServiceRunnerResponse {
	detail: string;
}

export interface LogResponse {
	lines: string[];
	total_lines: number;
}

export interface StartServiceRunnerRequest {
	period_hours: number;
}

export interface StartJobScraperServiceRunnerRequest extends StartServiceRunnerRequest {
	timedelta_days: number;
}

// Base interface with multiple call signatures for start method
export interface BaseServiceApi {
	getStatus: (token: string) => ApiResponsePromise<ServiceStatus>;
	stop: (token: string) => ApiResponsePromise<ServiceRunnerResponse>;
	getLogs: (lines: number, token: string) => ApiResponsePromise<LogResponse>;
}

// Specific interfaces extending the base
interface JobScraperServiceRunnerApi extends BaseServiceApi {
	start(periodHours: number, timedeltaDays: number, token: string): ApiResponsePromise<ServiceRunnerResponse>;
}

interface JobRatingServiceRunnerApi extends BaseServiceApi {
	start(periodHours: number, token: string): ApiResponsePromise<ServiceRunnerResponse>;
}

// Factory function to create service API objects
function createServiceApi(servicePath: string): BaseServiceApi {
	return {
		getStatus: async (token: string): ApiResponsePromise<ServiceStatus> => {
			return serviceApi.get(`${servicePath}/status`, token);
		},

		stop: async (token: string): ApiResponsePromise<ServiceRunnerResponse> => {
			return serviceApi.post(`${servicePath}/stop`, {}, token);
		},

		getLogs: async (lines: number, token: string): ApiResponsePromise<LogResponse> => {
			return serviceApi.get(`${servicePath}/logs?lines=${lines}`, token);
		},
	};
}

// Create the specific API instances
export const jobScraperServiceApi: JobScraperServiceRunnerApi = {
	...createServiceApi("job-scraper-service"),
	start: async (
		periodHours: number,
		timedeltaDays: number,
		token: string
	): ApiResponsePromise<ServiceRunnerResponse> => {
		const data: StartJobScraperServiceRunnerRequest = {
			period_hours: periodHours,
			timedelta_days: timedeltaDays,
		};
		return serviceApi.post("job-scraper-service/start", data, token);
	},
};

export const jobRatingServiceRunnerApi: JobRatingServiceRunnerApi = {
	...createServiceApi("job-rating-service-runner"),
	start: async (periodHours: number, token: string): ApiResponsePromise<ServiceRunnerResponse> => {
		const data: StartServiceRunnerRequest = { period_hours: periodHours };
		return serviceApi.post("job-rating-service-runner/start", data, token);
	},
};

export const aiSystemPromptsApi: CrudApi<AiSystemPromptData> = createCrudApi("ai-system-prompts");
