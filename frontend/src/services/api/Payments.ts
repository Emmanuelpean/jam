import { api, ApiResponsePromise } from "./Base";

export interface SubscriptionStatus {
	status: string | null;
	trial_end: Date | null;
}

export interface PortalSessionResponse {
	url: string;
}

export interface CheckoutSessionResponse {
	clientSecret: string;
}

export interface PaymentsApi {
	getSubscriptionStatus: (subscriptionId: string, token: string) => ApiResponsePromise<SubscriptionStatus>;
	createPortalSession: (customerEmail: string) => ApiResponsePromise<PortalSessionResponse>;
	createSubscriptionCheckout: (token: string) => ApiResponsePromise<CheckoutSessionResponse>;
}

export const paymentsApi: PaymentsApi = {
	getSubscriptionStatus: async (subscriptionId: string, token: string): ApiResponsePromise<SubscriptionStatus> => {
		return api.get(`payments/subscription-status/${subscriptionId}`, token);
	},

	createPortalSession: async (customerEmail: string): ApiResponsePromise<PortalSessionResponse> => {
		return api.post("payments/create-portal-session", { customer_email: customerEmail });
	},

	createSubscriptionCheckout: async (token: string): ApiResponsePromise<CheckoutSessionResponse> => {
		return api.post("payments/create-subscription-checkout", {}, token);
	},
};
