import { ApiError } from "./ApiError";
import { parseDates } from "../../utils/TimeUtils";

export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export const API_SERVICE_URL: string = import.meta.env.VITE_API_SERVICE_URL || "http://localhost:8001";

const parseResponseBody = async (response: Response): Promise<any> => {
	if (response.status === 204) {
		return null;
	}

	const contentType: string = response.headers.get("content-type") || "";

	if (contentType.includes("application/json")) {
		return response.json();
	}

	if (contentType.includes("text/")) {
		return response.text();
	}

	return response.blob();
};

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

const handleResponse = async <T>(response: Response, responseType?: boolean): Promise<ApiResponse<T>> => {
	const rawData: any = responseType ? await response.blob() : await parseResponseBody(response);

	if (!response.ok) {
		const message: string =
			(rawData && (rawData.message || rawData.detail)) || `Request failed with status ${response.status}`;
		throw new ApiError(message, response.status, rawData);
	}

	const data: any = responseType ? rawData : parseDates(rawData);

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

	async patch(endpoint: string, data: any, token: string | null = null): ApiResponsePromise {
		const response: Response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "PATCH",
			headers: getAuthHeaders(token || ""),
			body: JSON.stringify(data),
		});
		return handleResponse(response);
	}

	async delete(endpoint: string, token: string | null = null, data: any = null): ApiResponsePromise {
		const response: Response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "DELETE",
			headers: getAuthHeaders(token || ""),
			...(data && { body: JSON.stringify(data) }),
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
