import React, { JSX, useCallback, useEffect } from "react";
import { Modal } from "react-bootstrap";
import { loadStripe } from "@stripe/stripe-js";
import { EmbeddedCheckout, EmbeddedCheckoutProvider } from "@stripe/react-stripe-js";
import { ApiResponse } from "../../services/api/Base";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAuth } from "../../contexts/AuthContext";
import { CheckoutSessionResponse, paymentsApi } from "../../services/api/Payments";

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || "");

interface CheckoutModalProps {
	show: boolean;
	onHide: (refetchUser: boolean) => void;
	userEmail: string;
}

export const StripeCheckoutModal: React.FC<CheckoutModalProps> = ({
	show,
	onHide,
}: CheckoutModalProps): JSX.Element => {
	const { showToastSuccess } = useGlobalToast();
	const { token } = useAuth();

	const fetchClientSecret = useCallback(async (): Promise<string> => {
		if (!token) throw new Error("No authentication token");

		try {
			const response: ApiResponse<CheckoutSessionResponse> = await paymentsApi.createSubscriptionCheckout(token);
			if (!response.data.clientSecret) {
				new Error("No clientSecret in response");
			}
			return response.data.clientSecret;
		} catch (error) {
			console.error("fetchClientSecret error:", error);
			throw error;
		}
	}, [token]);

	useEffect(() => {
		if (!show) return;

		const interval = setInterval(() => {
			document.querySelectorAll('div[style*="2147483647"]').forEach((el) => el.remove());
		}, 200);

		return () => clearInterval(interval);
	}, [show]);

	// noinspection JSUnusedGlobalSymbols
	const options = {
		fetchClientSecret,
		onComplete: async (): Promise<void> => {
			showToastSuccess("Subscription successful! It might take a few moments to update your account.");
			onHide(true);
		},
	};

	return (
		<Modal
			show={show}
			onHide={() => onHide(false)}
			size="lg"
			centered={true}
			backdrop="static"
			id={"stripe-checkout-modal"}
		>
			<Modal.Header closeButton>
				<Modal.Title>Subscribe to TOAST</Modal.Title>
			</Modal.Header>

			<Modal.Body style={{ minHeight: "500px", position: "relative", zIndex: 1 }}>
				{show && (
					<EmbeddedCheckoutProvider stripe={stripePromise} options={options}>
						<EmbeddedCheckout />
					</EmbeddedCheckoutProvider>
				)}
			</Modal.Body>
		</Modal>
	);
};
