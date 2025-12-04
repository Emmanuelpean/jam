import { ServiceLog } from "./Schemas";

export interface ApiError extends Error {
	status?: number;
	data?: any;
}

interface QueryParams {
	[key: string]: any;
}

interface RequestOptions {
	responseType?: "blob" | "json";
}

interface CrudApi {
	getAll: (token: string, queryParams?: QueryParams | null) => Promise<any>;
	get: (id: number, token: string) => Promise<any>;
	create: (data: any, token: string) => Promise<any>;
	update: (id: number, data: any, token: string) => Promise<any>;
	delete: (id: number, token: string) => Promise<any>;
}

interface ScrapedJobCrudApi extends CrudApi {
	getCount: (token: string) => Promise<any>;
}

interface ExportCrudApi {
	download: (filename: string, token: string) => Promise<void>;
}

interface EisServiceLogCrudApi extends CrudApi {
	getLatest: (token: string) => Promise<ServiceLog>;
}

interface AuthApi {
	login: (email: string, password: string) => Promise<any>;
	register: (email: string, password: string) => Promise<any>;
	getCurrentUser: (token: string) => Promise<any>;
	updateCurrentUser: (data: any, token: string) => Promise<any>;
	verifyEmail: (token: string) => Promise<any>;
	verifyNewEmail: (token: string) => Promise<any>;
	checkPendingEmail: (token: string) => Promise<any>;
	requestPasswordReset: (email: string) => Promise<any>;
	resetPassword: (token: string, newPassword: string) => Promise<{ message: string }>;
}

const API_BASE_URL: string = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const getAuthHeaders = (token: string): HeadersInit => ({
	"Content-Type": "application/json",
	...(token && { Authorization: `Bearer ${token}` }),
});

const handleResponse = async (response: Response, isBlob: boolean = false): Promise<any> => {
	// Enhanced error handling
	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
		const error: ApiError = new Error(errorData.detail);
		error.status = response.status;
		error.data = errorData;
		throw error;
	}

	if (isBlob) {
		return response.blob();
	}

	// Handle empty responses (like DELETE 204 No Content)
	const contentType = response.headers.get("content-type");
	if (response.status === 204 || !contentType || !contentType.includes("application/json")) {
		return null;
	}

	// Check if response has content before parsing JSON
	const text = await response.text();
	if (!text) {
		return null;
	}

	try {
		return JSON.parse(text);
	} catch (error) {
		console.warn("Failed to parse JSON response:", text);
		return null;
	}
};

class ApiService {
	async get(endpoint: string, token: string | null = null, options: RequestOptions = {}): Promise<any> {
		const response: Response = await fetch(`${API_BASE_URL}/${endpoint}`, {
			method: "GET",
			headers: getAuthHeaders(token || ""),
		});
		return handleResponse(response, options.responseType === "blob");
	}

	async post(endpoint: string, data: any, token: string | null = null): Promise<any> {
		const response: Response = await fetch(`${API_BASE_URL}/${endpoint}`, {
			method: "POST",
			headers: getAuthHeaders(token || ""),
			body: JSON.stringify(data),
		});
		return handleResponse(response);
	}

	async put(endpoint: string, data: any, token: string | null = null): Promise<any> {
		const response: Response = await fetch(`${API_BASE_URL}/${endpoint}`, {
			method: "PUT",
			headers: getAuthHeaders(token || ""),
			body: JSON.stringify(data),
		});
		return handleResponse(response);
	}

	async delete(endpoint: string, token: string | null = null): Promise<any> {
		const response: Response = await fetch(`${API_BASE_URL}/${endpoint}`, {
			method: "DELETE",
			headers: getAuthHeaders(token || ""),
		});
		return handleResponse(response);
	}

	async postFormData(endpoint: string, formData: FormData, token: string | null = null): Promise<any> {
		const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
		const response: Response = await fetch(`${API_BASE_URL}/${endpoint}`, {
			method: "POST",
			headers,
			body: formData,
		});
		return handleResponse(response);
	}

	async downloadFile(endpoint: string, filename: string, token: string | null = null): Promise<void> {
		// Use the existing get method with blob response type
		const blob = await this.get(endpoint, token, { responseType: "blob" });

		// Create download link and trigger download
		const url: string = window.URL.createObjectURL(blob);
		const link: HTMLAnchorElement = document.createElement("a");
		link.href = url;
		link.download = filename;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
		window.URL.revokeObjectURL(url);
	}
}

const api = new ApiService();

const createCrudApi = (endpoint: string): CrudApi => ({
	getAll: (token: string, queryParams: QueryParams | null = null): Promise<any> => {
		let url: string = `${endpoint}/`;
		if (queryParams) {
			const searchParams = new URLSearchParams();
			Object.keys(queryParams).forEach((key: string): void => {
				const value: any = queryParams[key];
				if (value !== undefined) {
					if (Array.isArray(value)) {
						value.forEach((item): void => {
							searchParams.append(key, String(item));
						});
					} else {
						searchParams.append(key, String(value));
					}
				}
			});
			if (searchParams.toString()) {
				url += `?${searchParams.toString()}`;
			}
		}
		return api.get(url, token);
	},
	get: (id: string | number, token: string): Promise<any> => api.get(`${endpoint}/${id}`, token),
	create: (data: any, token: string): Promise<any> => api.post(`${endpoint}/`, data, token),
	update: (id: string | number, data: any, token: string): Promise<any> => api.put(`${endpoint}/${id}`, data, token),
	delete: (id: string | number, token: string): Promise<any> => api.delete(`${endpoint}/${id}`, token),
});

export const jobsApi: CrudApi = createCrudApi("jobs");
export const companiesApi: CrudApi = createCrudApi("companies");
export const locationsApi: CrudApi = createCrudApi("locations");
export const keywordsApi: CrudApi = createCrudApi("keywords");
export const personsApi: CrudApi = createCrudApi("persons");
export const aggregatorsApi: CrudApi = createCrudApi("aggregators");
export const interviewsApi: CrudApi = createCrudApi("interviews");
export const jobApplicationUpdatesApi: CrudApi = createCrudApi("jobapplicationupdates");
export const userApi: CrudApi = createCrudApi("users");
export const settingsApi: CrudApi = createCrudApi("settings");
export const countriesApi: CrudApi = createCrudApi("others/countries");
export const currenciesApi: CrudApi = createCrudApi("others/currencies");

export const exportApi: ExportCrudApi = {
	download: (filename: string, token: string) => api.downloadFile("export/", filename, token),
};

export const scrapedJobApi: ScrapedJobCrudApi = {
	...createCrudApi("scraped_jobs"),
	getCount: (token: string): Promise<any> => api.get("scraped_jobs/count", token),
};

export const eisServiceLogApi: EisServiceLogCrudApi = {
	...createCrudApi("eis_service_logs"),
	getLatest: (token: string): Promise<ServiceLog> => api.get("eis_service_logs/latest", token),
};

export const authApi: AuthApi = {
	login: async (email: string, password: string) => {
		const formData = new FormData();
		formData.append("username", email);
		formData.append("password", password);
		return api.postFormData("login/", formData);
	},

	register: async (email: string, password: string) => {
		return api.post("register/", { email, password });
	},

	getCurrentUser: async (token: string) => {
		return api.get("current_user/", token);
	},

	updateCurrentUser: async (data: any, token: string) => {
		return api.put("current_user/", data, token);
	},

	checkPendingEmail: async (token: string) => {
		return api.get("current_user/check-pending-email/", token);
	},

	verifyEmail: async (token: string) => {
		return api.get(`register/verify-email/${token}`);
	},

	requestPasswordReset: async (email: string): Promise<{ message: string }> => {
		return api.post("password/forgot", { email });
	},

	verifyNewEmail: async (token: string) => {
		return api.get(`current_user/verify-email/${token}`);
	},

	resetPassword: async (token: string, newPassword: string): Promise<{ message: string }> => {
		return api.post("password/reset", {
			token,
			new_password: newPassword,
		});
	},
};

export type ThreadStatus = "started" | "stopped" | "starting" | "stopping";

export interface ScraperStatus {
	thread_status: ThreadStatus;
	scraper_running: boolean;
	period_hours: number | null;
	timedelta_days: number | null;
	sleep_until: Date | null;
}

export interface StartScraperRequest {
	period_hours: number;
	timedelta_days: number;
}

interface ScraperResponse {
	detail: string;
}

export interface LogResponse {
	lines: string[];
	total_lines: number;
}

interface JobScraperApi {
	getStatus: (token: string) => Promise<ScraperStatus>;
	start: (periodHours: number, timedeltaDays: number, token: string) => Promise<ScraperResponse>;
	stop: (token: string) => Promise<ScraperResponse>;
	getLogs: (lines: number, token: string) => Promise<LogResponse>;
}

export const jobScraperServiceApi: JobScraperApi = {
	getStatus: async (token: string): Promise<ScraperStatus> => {
		return api.get("email_scraper_service/status", token);
	},

	start: async (periodHours: number, timedeltaDays: number, token: string): Promise<ScraperResponse> => {
		const data: StartScraperRequest = { period_hours: periodHours, timedelta_days: timedeltaDays };
		return api.post("email_scraper_service/start", data, token);
	},

	stop: async (token: string): Promise<ScraperResponse> => {
		return api.post("email_scraper_service/stop", {}, token);
	},

	getLogs: async (lines: number, token: string): Promise<LogResponse> => {
		return api.get(`email_scraper_service/logs?lines=${lines}`, token);
	},
};

export { api };
