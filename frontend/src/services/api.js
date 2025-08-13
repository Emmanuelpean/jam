import { accessAttribute } from "../utils/Utils";

const API_BASE_URL = "http://localhost:8000";

// Helper function to get auth headers
const getAuthHeaders = (token) => ({
	"Content-Type": "application/json",
	...(token && { Authorization: `Bearer ${token}` }),
});

// Helper function to handle API responses
const handleResponse = async (response) => {
	if (!response.ok) {
		const errorData = await response.json().catch(() => ({}));
		const error = new Error(errorData.detail || `HTTP error! status: ${response.status}`);
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

// Generic API service class
class ApiService {
	constructor(baseUrl = API_BASE_URL) {
		this.baseUrl = baseUrl;
	}

	// Enhanced error handling helper for blob responses
	async handleResponseWithBlob(response, isBlob = false) {
		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			const error = new Error(errorData.detail || `HTTP error! status: ${response.status}`);
			error.status = response.status;
			error.data = errorData;
			throw error;
		}

		if (isBlob) {
			return response.blob();
		}

		return handleResponse(response);
	}

	async get(endpoint, token = null, options = {}) {
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "GET",
			headers: getAuthHeaders(token),
		});

		return this.handleResponseWithBlob(response, options.responseType === "blob");
	}

	// Generic POST request
	async post(endpoint, data, token = null) {
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "POST",
			headers: getAuthHeaders(token),
			body: JSON.stringify(data),
		});
		return handleResponse(response);
	}

	// Generic PUT request
	async put(endpoint, data, token = null) {
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "PUT",
			headers: getAuthHeaders(token),
			body: JSON.stringify(data),
		});
		return handleResponse(response);
	}

	// Generic PATCH request
	async patch(endpoint, data, token = null) {
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "PATCH",
			headers: getAuthHeaders(token),
			body: JSON.stringify(data),
		});
		return handleResponse(response);
	}

	// Generic DELETE request
	async delete(endpoint, token = null) {
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "DELETE",
			headers: getAuthHeaders(token),
		});
		return handleResponse(response);
	}

	// Form data POST (for login, etc.)
	async postFormData(endpoint, formData, token = null) {
		const headers = token ? { Authorization: `Bearer ${token}` } : {};
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "POST",
			headers,
			body: formData,
		});
		return handleResponse(response);
	}

	// Simplified download method using existing get method
	async downloadFile(endpoint, filename, token = null) {
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

// Create API service instance
const api = new ApiService();

// Authentication API
export const authApi = {
	login: async (email, password) => {
		const formData = new FormData();
		formData.append("username", email);
		formData.append("password", password);
		return api.postFormData("login", formData);
	},

	register: async (email, password) => {
		return api.post("users/", { email, password });
	},

	getCurrentUser: async (token) => {
		return api.get("users/me", token);
	},

	updateUserTheme: async (theme, token) => {
		return api.put("users/me", { theme }, token);
	},
};

const createCrudApi = (endpoint) => ({
	getAll: (token, queryParams = null) => {
		let url = `${endpoint}/`;
		if (queryParams) {
			const searchParams = new URLSearchParams();
			Object.keys(queryParams).forEach((key) => {
				if (queryParams[key] !== undefined) {
					searchParams.append(key, queryParams[key]);
				}
			});
			if (searchParams.toString()) {
				url += `?${searchParams.toString()}`;
			}
		}
		return api.get(url, token);
	},
	get: (id, token) => api.get(`${endpoint}/${id}`, token),
	create: (data, token) => api.post(`${endpoint}/`, data, token),
	update: (id, data, token) => api.put(`${endpoint}/${id}`, data, token),
	delete: (id, token) => api.delete(`${endpoint}/${id}`, token),
});

// Create all your APIs with the factory
export const jobsApi = createCrudApi("jobs");
export const companiesApi = createCrudApi("companies");
export const locationsApi = createCrudApi("locations");
export const keywordsApi = createCrudApi("keywords");
export const personsApi = createCrudApi("persons");
export const jobApplicationsApi = createCrudApi("jobapplications");
export const interviewsApi = createCrudApi("interviews");
export const aggregatorsApi = createCrudApi("aggregators");
export const jobAlertEmailApi = createCrudApi("jobalertemails");
export const scrapedJobApi = createCrudApi("scrapedjobs");
export const serviceLogApi = createCrudApi("servicelogs");
export const userApi = createCrudApi("users");

export { api, API_BASE_URL };

// Helper functions for common patterns
export const apiHelpers = {
	// Convert data to select options
	toSelectOptions: (data, valueKey = "id", labelKey = "name") => {
		return data.map((item) => ({
			value: accessAttribute(item, valueKey),
			label: accessAttribute(item, labelKey),
			data: item,
		}));
	},

	// Handle API errors consistently
	handleError: (error, defaultMessage = "An error occurred") => {
		console.error("API Error:", error);
		return {
			success: false,
			error: error.message || defaultMessage,
			status: error.status,
		};
	},

	// Handle API success consistently
	handleSuccess: (data, message = "Operation successful") => {
		return {
			success: true,
			data,
			message,
		};
	},

	// Batch API calls
	batchGet: async (endpoints, token) => {
		try {
			const promises = endpoints.map((endpoint) => api.get(endpoint, token));
			const results = await Promise.all(promises);
			return apiHelpers.handleSuccess(results);
		} catch (error) {
			return apiHelpers.handleError(error);
		}
	},
};

export const filesApi = {
	...createCrudApi("files"),

	// Method that returns blob for manual handling
	downloadBlob: (id, token) => api.get(`files/${id}/download`, token, { responseType: "blob" }),

	// Method that directly triggers browser download
	download: (id, filename, token) => api.downloadFile(`files/${id}/download`, filename, token),
};

export const themesApi = {
	getAll: () => {
		// This could be a static API endpoint or just return the themes
		return Promise.resolve([
			{ key: "strawberry", name: "Strawberry", description: "Sweet and vibrant" },
			{ key: "blueberry", name: "Blueberry", description: "Deep and rich" },
			{ key: "raspberry", name: "Raspberry", description: "Tart and bold" },
			{ key: "mixed-berry", name: "Mixed Berry", description: "Complex and layered" },
			{ key: "forest-berry", name: "Forest Berry", description: "Natural and earthy" },
			{ key: "blackberry", name: "Blackberry", description: "Deep and sophisticated" },
		]);
	},
	getRandomTheme: async () => {
		const themes = await themesApi.getAll();
		return themes[Math.floor(Math.random() * themes.length)];
	},
};
