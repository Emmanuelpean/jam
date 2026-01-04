import React, { useCallback, useEffect, JSX, useRef } from "react";
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
	const sessionIdRef = useRef<string | null>(null);

	const fetchClientSecret = useCallback(async () => {
		try {
			const response: Response = await fetch(API_BASE_URL + "/payments/create-subscription-checkout", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ customer_email: userEmail }),
			});

			if (!response.ok) {
				new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			// Extract and store session ID from client_secret
			sessionIdRef.current = data.clientSecret.split("_secret_")[0];
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
		onComplete: async () => {
			if (sessionIdRef.current) {
				await fetch(`${API_BASE_URL}/payments/check-subscription/${sessionIdRef.current}`);
			}
			fetchUserInfo(token!).then(() => {
				showToastSuccess("Subscription successful! Enjoy your premium features!");
				onHide();
			});
		},
	};

	return (
		<Modal show={show} onHide={onHide} size="lg" centered={true} backdrop="static">
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
