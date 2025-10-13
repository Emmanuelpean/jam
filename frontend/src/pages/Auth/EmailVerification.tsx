import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, Spinner, Alert } from "react-bootstrap";
import { ReactComponent as JamLogo } from "../../assets/Logo.svg";
import "./Auth.css";
import { authApi, ApiError } from "../../services/Api";

interface VerificationResponse {
	message: string;
}

function EmailVerification(): React.ReactElement {
	const { token } = useParams<{ token: string }>();
	const navigate = useNavigate();
	const [verifying, setVerifying] = useState<boolean>(true);
	const [success, setSuccess] = useState<boolean>(false);
	const [error, setError] = useState<string>("");

	useEffect((): void => {
		const verifyEmail = async () => {
			if (!token) {
				setError("Invalid verification link - token missing");
				setVerifying(false);
				return;
			}

			try {
				const response: VerificationResponse = await authApi.verifyEmail(token);

				setSuccess(true);
				setError("");

				// Redirect to login after 3 seconds
				setTimeout(() => {
					navigate("/login", {
						state: { message: "Email verified! Please log in." },
					});
				}, 3000);
			} catch (err: any) {
				const apiError = err as ApiError;
				const errorMessage =
					apiError.data?.detail ||
					apiError.message ||
					"Failed to verify email. The link may be invalid or expired.";
				setError(errorMessage);
				setSuccess(false);
			} finally {
				setVerifying(false);
			}
		};

		verifyEmail();
	}, [token, navigate]);

	useEffect(() => {
		document.documentElement.setAttribute("data-theme", "mixed-berry");
	}, []);

	return (
		<div className="auth-container">
			<div className="auth-logo">
				<div className="logo-container logo-container-vertical">
					<JamLogo style={{ height: "175px", width: "auto" }} />
					<div className="logo-text-below text-gradient-primary" style={{ fontSize: "50px" }}>
						Job Application Manager
					</div>
				</div>
			</div>

			<Card className="auth-card border-0 auth-card-animated">
				<Card.Body className="text-center">
					<Card.Title className="text-primary mb-4">Email Verification</Card.Title>

					{verifying && (
						<div className="d-flex flex-column align-items-center">
							<Spinner animation="border" variant="primary" className="mb-3" />
							<p className="text-muted">Verifying your email address...</p>
						</div>
					)}

					{!verifying && success && (
						<Alert variant="success" className="mb-0">
							<Alert.Heading className="h6 d-flex align-items-center justify-content-center mb-2">
								<i className="bi bi-check-circle-fill me-2"></i>
								Email Verified Successfully!
							</Alert.Heading>
							<p className="mb-2">Your email has been verified.</p>
							<p className="mb-0 small text-muted">Redirecting to login page...</p>
						</Alert>
					)}

					{!verifying && error && (
						<>
							<Alert variant="danger" className="mb-3">
								<Alert.Heading className="h6 d-flex align-items-center justify-content-center mb-2">
									<i className="bi bi-x-circle-fill me-2"></i>
									Verification Failed
								</Alert.Heading>
								<p className="mb-0">{error}</p>
							</Alert>

							<button onClick={() => navigate("/login")} className="btn btn-primary">
								Go to Login
							</button>
						</>
					)}
				</Card.Body>
			</Card>
		</div>
	);
}

export default EmailVerification;
