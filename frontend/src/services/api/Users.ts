import { api, ApiResponsePromise } from "./Base";
import { UserData, UserQualification } from "../Schemas";
import { createCrudApi, CrudApi } from "./Crud";

export interface GenericResponse {
	success: boolean;
	message: string;
	error_code: number | null;
}

export interface AuthResponse {
	success: boolean;
	status?: number;
	error?: string;
}

export interface LoginResponse {
	access_token: string;
}

export interface UpdateCurrentUserResponse {
	user: UserData;
	success: boolean;
	message: string;
	logged_out: boolean;
}

export const userApi: CrudApi<UserData> = createCrudApi("users");

export interface AuthApi {
	login: (email: string, password: string) => ApiResponsePromise<LoginResponse>;
	register: (email: string, password: string) => ApiResponsePromise<GenericResponse>;
	getCurrentUser: (token: string) => ApiResponsePromise<UserData>;
	updateCurrentUser: (data: any, token: string) => ApiResponsePromise<UpdateCurrentUserResponse>;
	verifyEmail: (token: string) => ApiResponsePromise<GenericResponse>;
	verifyNewEmail: (token: string) => ApiResponsePromise<GenericResponse>;
	checkPendingEmail: (token: string) => ApiResponsePromise<boolean>;
	requestPasswordReset: (email: string) => ApiResponsePromise<GenericResponse>;
	resetPassword: (token: string, newPassword: string) => ApiResponsePromise<GenericResponse>;
}

export const authApi: AuthApi = {
	login: async (email: string, password: string): ApiResponsePromise<LoginResponse> => {
		const formData = new FormData();
		formData.append("username", email);
		formData.append("password", password);
		return api.postFormData("login/", formData);
	},

	register: async (email: string, password: string): ApiResponsePromise<GenericResponse> => {
		return api.post("register/", { email, password });
	},

	getCurrentUser: async (token: string): ApiResponsePromise<UserData> => {
		return api.get("current-user/", token);
	},

	updateCurrentUser: async (data: any, token: string): ApiResponsePromise<UpdateCurrentUserResponse> => {
		return api.put("current-user/", data, token);
	},

	checkPendingEmail: async (token: string): ApiResponsePromise<boolean> => {
		return api.get("current-user/check-pending-email/", token);
	},

	verifyEmail: async (token: string): ApiResponsePromise<GenericResponse> => {
		return api.get(`register/verify-email/${token}`);
	},

	requestPasswordReset: async (email: string): ApiResponsePromise<GenericResponse> => {
		return api.post("password/forgot", { email });
	},

	verifyNewEmail: async (token: string): ApiResponsePromise<GenericResponse> => {
		return api.get(`current-user/verify-email/${token}`);
	},

	resetPassword: async (token: string, newPassword: string): ApiResponsePromise<GenericResponse> => {
		return api.post("password/reset", {
			token,
			new_password: newPassword,
		});
	},
};

export interface UserQualificationApi {
	getLatest: (token: string) => ApiResponsePromise<UserQualification>;
	upsert: (data: any, token: string) => ApiResponsePromise<UserQualification>;
}

export const userQualificationApi: UserQualificationApi = {
	getLatest: (token: string): ApiResponsePromise<UserQualification> => api.get("user-qualifications/latest", token),
	upsert: (data: any, token: string): ApiResponsePromise<UserQualification> =>
		api.post("user-qualifications/", data, token),
};

export interface ExportCrudApi {
	download: (filename: string, token: string) => Promise<void>;
}

export const exportApi: ExportCrudApi = {
	download: (filename: string, token: string): Promise<void> => api.downloadFile("export/", filename, token),
};
