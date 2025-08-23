// Define types for better type safety
interface ApiError extends Error {
	status?: number;
	data?: any;
}

interface QueryParams {
	[key: string]: string | number | boolean | undefined;
}

interface RequestOptions {
	responseType?: "blob" | "json";
}

interface AuthHeaders {
	"Content-Type": string;
	Authorization?: string;
	[key: string]: string | undefined; // Add index signature for HeadersInit compatibility
}

interface CrudApi {
	getAll: (token: string, queryParams?: QueryParams | null) => Promise<any>;
	get: (id: string | number, token: string) => Promise<any>;
	create: (data: any, token: string) => Promise<any>;
	update: (id: string | number, data: any, token: string) => Promise<any>;
	delete: (id: string | number, token: string) => Promise<any>;
}

interface FilesApi extends CrudApi {
	download: (id: string | number, filename: string, token: string) => Promise<void>;
}

interface AuthApi {
	login: (email: string, password: string) => Promise<any>;
	register: (email: string, password: string) => Promise<any>;
	getCurrentUser: (token: string) => Promise<any>;
	updateCurrentUser: (data: any, token: string) => Promise<any>;
}

const API_BASE_URL = "http://localhost:8000";

const getAuthHeaders = (token: string): AuthHeaders => ({
	"Content-Type": "application/json",
	...(token && { Authorization: `Bearer ${token}` }),
});

const handleResponse = async (response: Response): Promise<any> => {
	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
		const error: ApiError = new Error(errorData.detail || `HTTP error! status: ${response.status}`);
		error.status = response.status;
		error.data = errorData;
		throw error;
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
	private baseUrl: string;

	constructor(baseUrl: string = API_BASE_URL) {
		this.baseUrl = baseUrl;
	}

	// Enhanced error handling helper for blob responses
	async handleResponseWithBlob(response: Response, isBlob: boolean = false): Promise<any> {
		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			const error: ApiError = new Error(errorData.detail || `HTTP error! status: ${response.status}`);
			error.status = response.status;
			error.data = errorData;
			throw error;
		}

		if (isBlob) {
			return response.blob();
		}

		return handleResponse(response);
	}

	async get(endpoint: string, token: string | null = null, options: RequestOptions = {}): Promise<any> {
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "GET",
			headers: getAuthHeaders(token || ""),
		});

		return this.handleResponseWithBlob(response, options.responseType === "blob");
	}

	// Generic POST request
	async post(endpoint: string, data: any, token: string | null = null): Promise<any> {
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "POST",
			headers: getAuthHeaders(token || ""),
			body: JSON.stringify(data),
		});
		return handleResponse(response);
	}

	// Generic PUT request
	async put(endpoint: string, data: any, token: string | null = null): Promise<any> {
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "PUT",
			headers: getAuthHeaders(token || ""),
			body: JSON.stringify(data),
		});
		return handleResponse(response);
	}

	// Generic PATCH request
	async patch(endpoint: string, data: any, token: string | null = null): Promise<any> {
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "PATCH",
			headers: getAuthHeaders(token || ""),
			body: JSON.stringify(data),
		});
		return handleResponse(response);
	}

	// Generic DELETE request
	async delete(endpoint: string, token: string | null = null): Promise<any> {
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "DELETE",
			headers: getAuthHeaders(token || ""),
		});
		return handleResponse(response);
	}

	// Form data POST (for login, etc.)
	async postFormData(endpoint: string, formData: FormData, token: string | null = null): Promise<any> {
		const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "POST",
			headers,
			body: formData,
		});
		return handleResponse(response);
	}

	// Simplified download method using existing get method
	async downloadFile(endpoint: string, filename: string, token: string | null = null): Promise<void> {
		// Use the existing get method with blob response type
		const blob = await this.get(endpoint, token, { responseType: "blob" });

		// Create download link and trigger download
		const url = window.URL.createObjectURL(blob);
		const link = document.createElement("a");
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
	getAll: (token: string, queryParams: QueryParams | null = null) => {
		let url = `${endpoint}/`;
		if (queryParams) {
			const searchParams = new URLSearchParams();
			Object.keys(queryParams).forEach((key) => {
				if (queryParams[key] !== undefined) {
					searchParams.append(key, String(queryParams[key]));
				}
			});
			if (searchParams.toString()) {
				url += `?${searchParams.toString()}`;
			}
		}
		return api.get(url, token);
	},
	get: (id: string | number, token: string) => api.get(`${endpoint}/${id}`, token),
	create: (data: any, token: string) => api.post(`${endpoint}/`, data, token),
	update: (id: string | number, data: any, token: string) => api.put(`${endpoint}/${id}`, data, token),
	delete: (id: string | number, token: string) => api.delete(`${endpoint}/${id}`, token),
});

export const jobsApi: CrudApi = createCrudApi("jobs");
export const companiesApi: CrudApi = createCrudApi("companies");
export const locationsApi: CrudApi = createCrudApi("locations");
export const keywordsApi: CrudApi = createCrudApi("keywords");
export const personsApi: CrudApi = createCrudApi("persons");
export const jobApplicationsApi: CrudApi = createCrudApi("jobapplications");
export const interviewsApi: CrudApi = createCrudApi("interviews");
export const aggregatorsApi: CrudApi = createCrudApi("aggregators");
export const jobAlertEmailApi: CrudApi = createCrudApi("jobalertemails");
export const scrapedJobApi: CrudApi = createCrudApi("scrapedjobs");
export const serviceLogApi: CrudApi = createCrudApi("servicelogs");
export const userApi: CrudApi = createCrudApi("users");

export const filesApi: FilesApi = {
	...createCrudApi("files"),
	download: (id: string | number, filename: string, token: string) =>
		api.downloadFile(`files/${id}/download`, filename, token),
};

export const authApi: AuthApi = {
	login: async (email: string, password: string) => {
		const formData = new FormData();
		formData.append("username", email);
		formData.append("password", password);
		return api.postFormData("login", formData);
	},

	register: async (email: string, password: string) => {
		return api.post("users/", { email, password });
	},

	getCurrentUser: async (token: string) => {
		return api.get("users/me", token);
	},

	updateCurrentUser: async (data: any, token: string) => {
		return api.put("users/me", data, token);
	},
};

export { api };
