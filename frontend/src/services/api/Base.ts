export const API_BASE_URL: string = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";
export const API_SERVICE_URL: string = process.env.REACT_APP_API_SERVICE_URL || "http://localhost:8001";

export interface ApiError extends Error {
	status?: number | null;
	data?: any;
}

export interface QueryParams {
	[key: string]: any;
}

export interface RequestOptions {
	responseType?: "blob" | "json";
}

const getAuthHeaders = (token: string): HeadersInit => ({
	"Content-Type": "application/json",
	...(token && { Authorization: `Bearer ${token}` }),
});

export interface ApiResponse<T = any> {
	data: T;
	status: number;
}

export type ApiResponsePromise<T = any> = Promise<ApiResponse<T>>;

const handleResponse = async (response: Response, isBlob: boolean = false): ApiResponsePromise => {
	// Enhanced error handling
	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
		const error: ApiError = new Error(errorData.detail);
		error.status = response.status;
		error.data = errorData;
		throw error;
	}

	let data: any;

	if (isBlob) {
		data = await response.blob();
	} else {
		// Check if response has content before parsing JSON
		const text: string = await response.text();
		if (!text) {
			data = null;
		} else {
			try {
				data = JSON.parse(text);
			} catch (error) {
				console.warn("Failed to parse JSON response:", text);
				data = null;
			}
		}
	}

	return {
		data,
		status: response.status,
	};
};

export class ApiService {
	private readonly baseUrl: string;

	constructor(baseUrl: string) {
		this.baseUrl = baseUrl;
	}

	async get(endpoint: string, token: string | null = null, options: RequestOptions = {}): ApiResponsePromise {
		const response: Response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "GET",
			headers: getAuthHeaders(token || ""),
		});
		return handleResponse(response, options.responseType === "blob");
	}

	async post(endpoint: string, data: any, token: string | null = null): ApiResponsePromise {
		const response: Response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "POST",
			headers: getAuthHeaders(token || ""),
			body: JSON.stringify(data),
		});
		return handleResponse(response);
	}

	async put(endpoint: string, data: any, token: string | null = null): ApiResponsePromise {
		const response: Response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "PUT",
			headers: getAuthHeaders(token || ""),
			body: JSON.stringify(data),
		});
		return handleResponse(response);
	}

	async delete(endpoint: string, token: string | null = null): ApiResponsePromise {
		const response: Response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "DELETE",
			headers: getAuthHeaders(token || ""),
		});
		return handleResponse(response);
	}

	async postFormData(endpoint: string, formData: FormData, token: string | null = null): ApiResponsePromise {
		const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
		const response: Response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "POST",
			headers,
			body: formData,
		});
		return handleResponse(response);
	}

	async downloadFile(endpoint: string, filename: string, token: string | null = null): Promise<void> {
		const blob = await this.get(endpoint, token, { responseType: "blob" });
		const url: string = window.URL.createObjectURL(blob.data);
		const link: HTMLAnchorElement = document.createElement("a");
		link.href = url;
		link.download = filename;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
		window.URL.revokeObjectURL(url);
	}
}

export const baseApi = new ApiService(API_BASE_URL);
export const serviceApi = new ApiService(API_SERVICE_URL);
