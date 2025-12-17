import { createCrudApi, CrudApi } from "./Base";
import { UserQualification } from "../Schemas";
import { api } from "./Base";

export const userApi: CrudApi = createCrudApi("users");

export interface AuthApi {
	login: (email: string, password: string) => Promise<any>;
	register: (email: string, password: string) => Promise<any>;
	getCurrentUser: (token: string) => Promise<any>;
	updateCurrentUser: (data: any, token: string) => Promise<any>;
	verifyEmail: (token: string) => Promise<any>;
	verifyNewEmail: (token: string) => Promise<any>;
	checkPendingEmail: (token: string) => Promise<any>;
	requestPasswordReset: (email: string) => Promise<any>;
	resetPassword: (token: string, newPassword: string) => Promise<{ message: string }>;
}

export const authApi: AuthApi = {
	login: async (email: string, password: string) => {
		const formData = new FormData();
		formData.append("username", email);
		formData.append("password", password);
		return api.postFormData("login/", formData);
	},

	register: async (email: string, password: string) => {
		return api.post("register/", { email, password });
	},

	getCurrentUser: async (token: string) => {
		return api.get("current_user/", token);
	},

	updateCurrentUser: async (data: any, token: string) => {
		return api.put("current_user/", data, token);
	},

	checkPendingEmail: async (token: string) => {
		return api.get("current_user/check-pending-email/", token);
	},

	verifyEmail: async (token: string) => {
		return api.get(`register/verify-email/${token}`);
	},

	requestPasswordReset: async (email: string): Promise<{ message: string }> => {
		return api.post("password/forgot", { email });
	},

	verifyNewEmail: async (token: string) => {
		return api.get(`current_user/verify-email/${token}`);
	},

	resetPassword: async (token: string, newPassword: string): Promise<{ message: string }> => {
		return api.post("password/reset", {
			token,
			new_password: newPassword,
		});
	},
};

export interface UserQualificationApi {
	getLatest: (token: string) => Promise<UserQualification>;
	upsert: (data: any, token: string) => Promise<UserQualification>;
}

export const userQualificationApi: UserQualificationApi = {
	getLatest: (token: string): Promise<UserQualification> => api.get("user_qualifications/latest", token),
	upsert: (data: any, token: string): Promise<UserQualification> => api.post("user_qualifications", data, token),
};

export interface ExportCrudApi {
	download: (filename: string, token: string) => Promise<void>;
}

export const exportApi: ExportCrudApi = {
	download: (filename: string, token: string) => api.downloadFile("export/", filename, token),
};
