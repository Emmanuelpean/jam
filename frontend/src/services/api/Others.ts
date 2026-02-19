import { ApiResponse, baseApi } from "./Base";
import { GeoLocationData } from "../schemas/Base";

export const emailApi = {
	fetchTemplateHtml: async (templateName: string, token: string): Promise<string> => {
		const response: ApiResponse<string> = await baseApi.get(`email-templates/preview/${templateName}`, token);
		return response.data;
	},
};

export const geolocationApi = {
	get: async (location: string, token: string): Promise<GeoLocationData> => {
		const response: ApiResponse<GeoLocationData> = await baseApi.post("geolocation", location, token);
		return response.data;
	},
};
