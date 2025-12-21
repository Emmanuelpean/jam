import { JobRatingServiceLog, JobScraperServiceLog } from "../Schemas";
import { api, createCrudApi, CrudApi } from "./Base";

// Scraped Job API
export interface ScrapedJobCrudApi extends CrudApi {
	getCount: (token: string) => Promise<any>;
}

export const scrapedJobApi: ScrapedJobCrudApi = {
	...createCrudApi("scraped_jobs"),
	getCount: (token: string): Promise<any> => api.get("scraped_jobs/count", token),
};

// Job Rating APIs
export const jobRatingApi: CrudApi = createCrudApi("job_ratings");

// Service Log APIs
export interface ServiceLogCrudApi extends CrudApi {
	getLatest: (token: string) => Promise<any>;
}

export const jobScraperServiceLogApi: ServiceLogCrudApi = {
	...createCrudApi("eis_service_logs"),
	getLatest: (token: string): Promise<JobScraperServiceLog> => api.get("eis_service_logs/latest", token),
};

export const jobRatingServiceLogApi: ServiceLogCrudApi = {
	...createCrudApi("job_rating_service_logs"),
	getLatest: (token: string): Promise<JobRatingServiceLog> => api.get("job_rating_service_logs/latest", token),
};

// Service Runner APIs
export type ThreadStatus = "started" | "stopped" | "starting" | "stopping";

export interface ServiceStatus {
	service_runner_status: ThreadStatus;
	service_running: boolean;
	service_kwargs: any;
	period_hours: number | null;
	sleep_until: Date | null;
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
	getStatus: (token: string) => Promise<ServiceStatus>;
	stop: (token: string) => Promise<ServiceRunnerResponse>;
	getLogs: (lines: number, token: string) => Promise<LogResponse>;
}

// Specific interfaces extending the base
interface JobScraperServiceRunnerApi extends BaseServiceApi {
	start(periodHours: number, timedeltaDays: number, token: string): Promise<ServiceRunnerResponse>;
}

interface JobRatingServiceRunnerApi extends BaseServiceApi {
	start(periodHours: number, token: string): Promise<ServiceRunnerResponse>;
}

// Factory function to create service API objects
function createServiceApi(servicePath: string): BaseServiceApi {
	return {
		getStatus: async (token: string): Promise<ServiceStatus> => {
			return api.get(`${servicePath}/status`, token);
		},

		stop: async (token: string): Promise<ServiceRunnerResponse> => {
			return api.post(`${servicePath}/stop`, {}, token);
		},

		getLogs: async (lines: number, token: string): Promise<LogResponse> => {
			return api.get(`${servicePath}/logs?lines=${lines}`, token);
		},
	};
}

// Create the specific API instances
export const jobScraperServiceApi: JobScraperServiceRunnerApi = {
	...createServiceApi("email_scraper_service"),
	start: async (periodHours: number, timedeltaDays: number, token: string): Promise<ServiceRunnerResponse> => {
		const data: StartJobScraperServiceRunnerRequest = { period_hours: periodHours, timedelta_days: timedeltaDays };
		return api.post("email_scraper_service/start", data, token);
	},
};

export const jobRatingServiceRunnerApi: JobRatingServiceRunnerApi = {
	...createServiceApi("job_rating_service_runner"),
	start: async (periodHours: number, token: string): Promise<ServiceRunnerResponse> => {
		const data: StartServiceRunnerRequest = { period_hours: periodHours };
		return api.post("job_rating_service_runner/start", data, token);
	},
};

// Filters
export const scrapedJobFilterApi: CrudApi = createCrudApi("scraped_job_filters");
