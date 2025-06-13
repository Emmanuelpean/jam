// Base configuration
// noinspection JSUnusedGlobalSymbols

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

	// Generic GET request
	async get(endpoint, token = null) {
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "GET",
			headers: getAuthHeaders(token),
		});
		return handleResponse(response);
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

	// Form data POST (for file uploads, login, etc.)
	async postFormData(endpoint, formData, token = null) {
		const headers = token ? { Authorization: `Bearer ${token}` } : {};
		const response = await fetch(`${this.baseUrl}/${endpoint}`, {
			method: "POST",
			headers,
			body: formData,
		});
		return handleResponse(response);
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

// Generic API factory function
const createCrudApi = (endpoint) => ({
	getAll: (token) => api.get(`${endpoint}/`, token),
	getById: (id, token) => api.get(`${endpoint}/${id}`, token),
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

export { api, API_BASE_URL };

// Helper functions for common patterns
export const apiHelpers = {

	// Convert data to select options
	toSelectOptions: (data, valueKey = "id", labelKey = "name") => {
		return data.map((item) => ({
			value: item[valueKey],
			label: item[labelKey],
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
	}
};
