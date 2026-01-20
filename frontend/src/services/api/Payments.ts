import { baseApi, ApiResponsePromise } from "./Base";

export interface SubscriptionStatus {
	status: string | null;
	trial_end: number | null;
}

export interface PortalSessionResponse {
	url: string;
}

export interface PaymentsApi {
	getSubscriptionStatus: (token: string) => ApiResponsePromise<SubscriptionStatus>;
	createPortalSession: (token: string) => ApiResponsePromise<PortalSessionResponse>;
	createSubscriptionCheckout: (token: string) => ApiResponsePromise<PortalSessionResponse>;
}

export const paymentsApi: PaymentsApi = {
	getSubscriptionStatus: async (token: string): ApiResponsePromise<SubscriptionStatus> => {
		return baseApi.get(`payments/subscription-status/`, token);
	},

	createPortalSession: async (token: string): ApiResponsePromise<PortalSessionResponse> => {
		return baseApi.post("payments/create-portal-session", {}, token);
	},

	createSubscriptionCheckout: async (
		token: string
	): ApiResponsePromise<PortalSessionResponse> => {
		return baseApi.post("payments/create-subscription-checkout", {}, token);
	},
};
