import { api, ApiResponsePromise } from "./Base";
import { createCrudApi, CrudApi } from "./Crud";
import {
	UserData,
	UserDataAccountUpdate,
	UserDataPreferencesUpdate,
	UserDataPremiumUpdate,
	UserQualification,
} from "../schemas/Core";

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

export const userApi: CrudApi<UserData> = createCrudApi("users");

export interface AuthApi {
	login: (email: string, password: string) => ApiResponsePromise<LoginResponse>;
	register: (registerData: RegisterData) => ApiResponsePromise<GenericResponse>;
	getCurrentUser: (token: string) => ApiResponsePromise<UserData>;
	updateCurrentUserAccount: (
		data: UserDataAccountUpdate,
		token: string,
	) => ApiResponsePromise<UpdateCurrentUserResponse>;
	updateCurrentUserPreferences: (
		data: UserDataPreferencesUpdate,
		token: string,
	) => ApiResponsePromise<GenericResponse>;
	updateCurrentUserPremium: (data: UserDataPremiumUpdate, token: string) => ApiResponsePromise<GenericResponse>;
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

	register: async (registerData: RegisterData): ApiResponsePromise<GenericResponse> => {
		return api.post("register/", registerData);
	},

	getCurrentUser: async (token: string): ApiResponsePromise<UserData> => {
		return api.get("current-user/", token);
	},

	updateCurrentUserAccount: async (
		data: UserDataAccountUpdate,
		token: string,
	): ApiResponsePromise<UpdateCurrentUserResponse> => {
		return api.put("current-user/account", data, token);
	},

	updateCurrentUserPreferences: async (
		data: UserDataPreferencesUpdate,
		token: string,
	): ApiResponsePromise<GenericResponse> => {
		return api.put("current-user/preferences", data, token);
	},

	updateCurrentUserPremium: async (
		data: UserDataPremiumUpdate,
		token: string,
	): ApiResponsePromise<GenericResponse> => {
		return api.put("current-user/premium", data, token);
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
