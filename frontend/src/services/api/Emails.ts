import { ApiResponse, baseApi } from "./Base";

export const emailApi = {
	fetchTemplateHtml: async (templateName: string, token: string): Promise<string> => {
		const response: ApiResponse<string> = await baseApi.get(`email-templates/preview/${templateName}`, token);
		return response.data;
	},
};
