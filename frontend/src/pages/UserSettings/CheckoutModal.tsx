import React, { useCallback, useEffect } from "react";
import { Modal } from "react-bootstrap";
import { loadStripe } from "@stripe/stripe-js";
import { EmbeddedCheckout, EmbeddedCheckoutProvider } from "@stripe/react-stripe-js";
import { API_BASE_URL } from "../../services/api/Base";

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || "");

interface CheckoutModalProps {
	show: boolean;
	onHide: () => void;
	userEmail: string;
}

export const CheckoutModal: React.FC<CheckoutModalProps> = ({ show, onHide, userEmail }) => {
	const fetchClientSecret = useCallback(async () => {
		try {
			const response = await fetch(API_BASE_URL + "/payments/create-subscription-checkout", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ customer_email: userEmail }),
			});

			if (!response.ok) {
				new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			console.log("Backend response:", data); // Debug log

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

	const options = { fetchClientSecret };

	return (
		<Modal show={show} onHide={onHide} size="lg" centered backdrop="static">
			<Modal.Header closeButton>
				<Modal.Title>Subscribe to TOAST Premium</Modal.Title>
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
