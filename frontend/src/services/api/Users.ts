import { ApiResponsePromise, baseApi } from "./Base";
import { createCrudApi, CrudApi } from "./Crud";
import { UserData, UserDataUpdate, UserQualification } from "../schemas/Core";

export interface GenericResponse {
	success: boolean;
	message: string;
	error_code: number | null;
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

export interface RegisterData {
	email: string;
	password: string;
	first_name: string;
	last_name: string;
}

export const userApi: CrudApi<UserData> & {
	invalidateAllSessions: (token: string) => ApiResponsePromise<GenericResponse>;
} = {
	...createCrudApi("users"),
	invalidateAllSessions: (token: string): ApiResponsePromise<GenericResponse> =>
		baseApi.post("users/invalidate-all-sessions", {}, token),
};

export interface AuthApi {
	login: (email: string, password: string) => ApiResponsePromise<LoginResponse>;
	register: (registerData: RegisterData) => ApiResponsePromise<GenericResponse>;
	getCurrentUser: (token: string) => ApiResponsePromise<UserData>;
	updateCurrentUser: (data: UserDataUpdate, token: string) => ApiResponsePromise<UpdateCurrentUserResponse>;
	verifyEmail: (token: string) => ApiResponsePromise<GenericResponse>;
	verifyNewEmail: (token: string) => ApiResponsePromise<GenericResponse>;
	checkPendingEmail: (token: string) => ApiResponsePromise<boolean>;
	requestPasswordReset: (email: string) => ApiResponsePromise<GenericResponse>;
	resetPassword: (token: string, newPassword: string) => ApiResponsePromise<GenericResponse>;
	deleteAccount: (password: string, token: string) => ApiResponsePromise<GenericResponse>;
}

export const authApi: AuthApi = {
	login: async (email: string, password: string): ApiResponsePromise<LoginResponse> => {
		const formData = new FormData();
		formData.append("username", email);
		formData.append("password", password);
		return baseApi.postFormData("login/", formData);
	},

	register: async (registerData: RegisterData): ApiResponsePromise<GenericResponse> => {
		return baseApi.post("register/", registerData);
	},

	getCurrentUser: async (token: string): ApiResponsePromise<UserData> => {
		return baseApi.get("current-user/", token);
	},

	updateCurrentUser: async (data: UserDataUpdate, token: string): ApiResponsePromise<UpdateCurrentUserResponse> => {
		return baseApi.put("current-user/", data, token);
	},

	checkPendingEmail: async (token: string): ApiResponsePromise<boolean> => {
		return baseApi.get("current-user/check-pending-email/", token);
	},

	verifyEmail: async (token: string): ApiResponsePromise<GenericResponse> => {
		return baseApi.get(`register/verify-email/${token}`);
	},

	requestPasswordReset: async (email: string): ApiResponsePromise<GenericResponse> => {
		return baseApi.post("password/forgot", { email });
	},

	verifyNewEmail: async (token: string): ApiResponsePromise<GenericResponse> => {
		return baseApi.get(`current-user/verify-email/${token}`);
	},

	resetPassword: async (token: string, newPassword: string): ApiResponsePromise<GenericResponse> => {
		return baseApi.post("password/reset", {
			token,
			new_password: newPassword,
		});
	},

	deleteAccount: async (password: string, token: string): ApiResponsePromise<GenericResponse> => {
		return baseApi.delete("current-user/", token, { password });
	},
};

export interface UserQualificationApi {
	getLatest: (token: string) => ApiResponsePromise<UserQualification>;
	upsert: (data: any, token: string) => ApiResponsePromise<UserQualification>;
}

export const userQualificationApi: UserQualificationApi = {
	getLatest: (token: string): ApiResponsePromise<UserQualification> =>
		baseApi.get("user-qualifications/latest", token),
	upsert: (data: any, token: string): ApiResponsePromise<UserQualification> =>
		baseApi.post("user-qualifications/", data, token),
};

export interface ExportCrudApi {
	download: (filename: string, token: string) => Promise<void>;
}

export const exportApi: ExportCrudApi = {
	download: (filename: string, token: string): Promise<void> => baseApi.downloadFile("export/", filename, token),
};
