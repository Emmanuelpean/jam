const API_BASE_URL = "http://localhost:8000";

const getAuthHeaders = (token) => ({
	"Content-Type": "application/json",
	...(token && { Authorization: `Bearer ${token}` }),
});

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

const api = new ApiService();

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
export const filesApi = {
	...createCrudApi("files"),

	download: (id, filename, token) => api.downloadFile(`files/${id}/download`, filename, token),
};
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

	updateCurrentUser: async (data, token) => {
		return api.put("users/me", data, token);
	},
};

export { api };
