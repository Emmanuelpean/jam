import { api, ApiResponsePromise, QueryParams } from "./Base";

export interface CrudApi<T = any> {
	getAll: (token: string, queryParams?: QueryParams | null) => ApiResponsePromise<T[]>;
	get: (id: number, token: string) => ApiResponsePromise<T>;
	create: (data: any, token: string) => ApiResponsePromise<T>;
	update: (id: number, data: any, token: string) => ApiResponsePromise<T>;
	delete: (id: number, token: string) => ApiResponsePromise<null>;
}

export const createCrudApi = <T = any>(endpoint: string): CrudApi<T> => ({
	getAll: (token: string, queryParams: QueryParams | null = null): ApiResponsePromise<T[]> => {
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
	get: (id: number, token: string): ApiResponsePromise<T> => api.get(`${endpoint}/${id}`, token),
	create: (data: any, token: string): ApiResponsePromise<T> => api.post(`${endpoint}/`, data, token),
	update: (id: number, data: any, token: string): ApiResponsePromise<T> => api.put(`${endpoint}/${id}`, data, token),
	delete: (id: number, token: string): ApiResponsePromise<null> => api.delete(`${endpoint}/${id}`, token),
});
