const API_BASE_URL: string = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

export interface ApiError extends Error {
	status?: number;
	data?: any;
}

export interface QueryParams {
	[key: string]: any;
}

export interface RequestOptions {
	responseType?: "blob" | "json";
}

export interface CrudApi {
	getAll: (token: string, queryParams?: QueryParams | null) => Promise<any>;
	get: (id: number, token: string) => Promise<any>;
	create: (data: any, token: string) => Promise<any>;
	update: (id: number, data: any, token: string) => Promise<any>;
	delete: (id: number, token: string) => Promise<any>;
}

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

export const createCrudApi = (endpoint: string): CrudApi => ({
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

export { api };
