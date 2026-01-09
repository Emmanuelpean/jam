import React, { useCallback, useEffect, JSX } from "react";
import { Modal } from "react-bootstrap";
import { loadStripe } from "@stripe/stripe-js";
import { EmbeddedCheckout, EmbeddedCheckoutProvider } from "@stripe/react-stripe-js";
import { API_BASE_URL } from "../../services/api/Base";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAuth } from "../../contexts/AuthContext";

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || "");

interface CheckoutModalProps {
	show: boolean;
	onHide: () => void;
	userEmail: string;
}

export const CheckoutModal: React.FC<CheckoutModalProps> = ({
	show,
	onHide,
	userEmail,
}: CheckoutModalProps): JSX.Element => {
	const { showToastSuccess } = useGlobalToast();
	const { fetchUserInfo, token } = useAuth();

	const fetchClientSecret = useCallback(async () => {
		try {
			// Check if running in test mode
			const isTestMode = process.env.REACT_APP_TEST_MODE === "true";
			const endpoint = isTestMode
				? "/test/create-subscription-checkout/" + process.env.REACT_APP_STRIPE_TEST_USER
				: "/payments/create-subscription-checkout";

			const response: Response = await fetch(API_BASE_URL + endpoint, {
				method: "POST",
				headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
			});

			if (!response.ok) {
				new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			if (!data.clientSecret) {
				new Error("No clientSecret in response");
			}

			return data.clientSecret;
		} catch (error) {
			console.error("fetchClientSecret error:", error);
			throw error;
		}
	}, [userEmail]);

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
			await fetchUserInfo(token!);
			showToastSuccess("Subscription successful! Enjoy your premium features!");
			onHide();
		},
	};

	return (
		<Modal show={show} onHide={onHide} size="lg" centered={true} backdrop="static" id={"stripe-checkout-modal"}>
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
