import { ApiResponsePromise, baseApi } from "./Base";

export interface PortalSessionResponse {
	url: string;
}

export interface PaymentsApi {
	createPortalSession: (token: string) => ApiResponsePromise<PortalSessionResponse>;
	createSubscriptionCheckout: (token: string) => ApiResponsePromise<PortalSessionResponse>;
}

export const paymentsApi: PaymentsApi = {
	createPortalSession: async (token: string): ApiResponsePromise<PortalSessionResponse> => {
		return baseApi.post("payments/create-portal-session", {}, token);
	},

	createSubscriptionCheckout: async (token: string): ApiResponsePromise<PortalSessionResponse> => {
		return baseApi.post("payments/create-subscription-checkout", {}, token);
	},
};
