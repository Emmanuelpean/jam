import { ApiResponse, baseApi } from "./Base";
import { Config, GeoLocationData, Status } from "../schemas/Base";

export const emailApi = {
	fetchTemplateHtml: async (templateName: string, token: string): Promise<string> => {
		const response: ApiResponse<string> = await baseApi.get(`email-templates/preview/${templateName}`, token);
		return response.data;
	},
};

export const geolocationApi = {
	get: async (location: string, token: string): Promise<GeoLocationData> => {
		const response: ApiResponse<GeoLocationData> = await baseApi.post("geolocation/", location, token);
		return response.data;
	},
};

export const configApi = {
	get: async (): Promise<Config> => {
		const response: ApiResponse<Config> = await baseApi.get("config/", null);
		return response.data;
	},
	getStatus: async (): Promise<Status> => {
		const response: ApiResponse<Status> = await baseApi.get("config/status/", null);
		return response.data;
	},
};

export const tourApi = {
	clearAll: async (token: string): Promise<void> => {
		await baseApi.post("tour/clear-all", {}, token);
	},
};
