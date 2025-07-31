import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import "./AuthForm.css";
import "../../Logo.css";
import { ReactComponent as JamLogo } from "../../assets/Logo.svg";
import { Button, Form, Alert, Card, Spinner } from "react-bootstrap";
import TermsAndConditions from "./TermsConditions";

function AuthForm() {
	const [isLogin, setIsLogin] = useState(true);
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");
	const [acceptedTerms, setAcceptedTerms] = useState(false);
	const [showTerms, setShowTerms] = useState(false);
	const [error, setError] = useState("");
	const [loading, setLoading] = useState(false);
	const [fieldErrors, setFieldErrors] = useState({});
    const { login, register, isAuthenticated } = useAuth();
	const navigate = useNavigate();
	const location = useLocation();

	useEffect(() => {
        // Redirect authenticated users to dashboard
        if (isAuthenticated) {
            navigate("/dashboard", { replace: true });
            return;
        }

		document.documentElement.setAttribute("data-theme", "mixed-berry");
		// Set form mode based on current path
		setIsLogin(location.pathname === "/login");
    }, [location.pathname, isAuthenticated, navigate]);

	const switchMode = () => {
		setIsLogin(!isLogin);
		setError("");
		setFieldErrors({});
		// Clear confirm password and terms when switching to login
		if (!isLogin) {
			setConfirmPassword("");
			setAcceptedTerms(false);
		}
		// Update URL without navigation
		window.history.replaceState(null, "", isLogin ? "/register" : "/login");
	};

	const resetForm = () => {
		setEmail("");
		setPassword("");
		setConfirmPassword("");
		setAcceptedTerms(false);
		setError("");
		setFieldErrors({});
	};

	const validateForm = () => {
		const errors = {};

		// Email validation
		if (!email || !email.includes("@")) {
			errors.email = "Please provide a valid email address.";
		}

		// Password validation
		if (!password) {
			errors.password = "Password is required.";
		} else if (!isLogin && password.length < 8) {
			errors.password = "Password must be at least 8 characters long.";
		}

		// Confirm password validation (only for register)
		if (!isLogin) {
			if (!confirmPassword) {
				errors.confirmPassword = "Please confirm your password.";
			} else if (password !== confirmPassword) {
				errors.confirmPassword = "Passwords do not match.";
			}

			// Terms acceptance validation (only for register)
			if (!acceptedTerms) {
				errors.terms = "You must accept the Terms and Conditions to register.";
			}
		}

		return errors;
	};

	async function handleSubmit(e) {
		e.preventDefault();

		// Validate form
		const errors = validateForm();
		setFieldErrors(errors);

		if (Object.keys(errors).length > 0) {
			return;
		}

		setError("");
		setLoading(true);

		try {
			if (isLogin) {
				const result = await login(email, password);
				if (result.success) {
					navigate("/dashboard");
				} else {
					if ([404, 403].includes(result.status)) {
						setError("Incorrect email or password");
					} else {
						setError("Failed to login. An unknown error occurred");
					}
				}
			} else {
				const result = await register(email, password);
				if (result.success) {
					setError("");
					setIsLogin(true);
					resetForm();
					window.history.replaceState(null, "", "/login");
					// Show success message briefly
					setError("Account created successfully! Please log in.");
					setTimeout(() => setError(""), 3000);
				} else {
					setError(typeof result.error === 'object' ?
						JSON.stringify(result.error) : result.error || 'Registration failed');
				}
			}
		} catch (error) {
			setError(isLogin ? "Failed to login. An unknown error occurred" : "Failed to create an account");
		}

		setLoading(false);
	}

    // Show loading state while checking authentication
    if (isAuthenticated) {
        return (
            <div className="auth-container">
                <div className="d-flex flex-column align-items-center">
                    <Spinner animation="border" variant="primary" />
                    <p className="mt-3 text-muted">Redirecting to dashboard...</p>
                </div>
            </div>
        );
    }

	return (
		<div className="auth-container">
			<div className="auth-logo">
				<div className="logo-container logo-container-vertical">
					<JamLogo style={{ height: "175px", width: "auto" }} alt="Logo" />
					<div className="logo-text logo-text-below text-gradient-primary">Job Application Manager</div>
				</div>
			</div>

			<Card className="auth-card border-0 auth-card-animated">
				<Card.Body>
					<Card.Title className="text-primary">
						{isLogin ? "Login" : "Create Account"}
					</Card.Title>

					{error && (
						<Alert
							variant={error.includes("successfully") ? "success" : "danger"}
							className="d-flex align-items-center"
						>
							<i className={`bi ${error.includes("successfully") ? "bi-check-circle-fill" : "bi-exclamation-triangle-fill"} me-2`}></i>
							{error}
						</Alert>
					)}

					<Form onSubmit={handleSubmit} autoComplete="on">
						<Form.Group className="mb-3" controlId="email">
							<Form.Label>
								<i className="bi bi-envelope-fill me-2 text-muted"></i>
								Email Address
							</Form.Label>
							<Form.Control
								type="email"
								name="email"
								placeholder="Enter your email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								size="lg"
								isInvalid={!!fieldErrors.email}
								autoComplete="email"
							/>
							{fieldErrors.email && (
								<div className="invalid-feedback">
									{fieldErrors.email}
								</div>
							)}
						</Form.Group>

						<Form.Group className="mb-3" controlId="password">
							<Form.Label>
								<i className="bi bi-lock-fill me-2 text-muted"></i>
								Password
							</Form.Label>
							<Form.Control
								type="password"
								name={isLogin ? "current-password" : "new-password"}
								placeholder="Enter your password"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								size="lg"
								isInvalid={!!fieldErrors.password}
								autoComplete={isLogin ? "current-password" : "new-password"}
							/>
							{fieldErrors.password && (
								<div className="invalid-feedback">
									{fieldErrors.password}
								</div>
							)}
							{!isLogin && !fieldErrors.password && (
								<Form.Text className="text-muted">
									Password must be at least 8 characters long
								</Form.Text>
							)}
						</Form.Group>

						{/* Always render confirm password field but control visibility with CSS */}
						<div className={`auth-field-container ${!isLogin ? 'auth-field-visible' : 'auth-field-hidden'}`}>
							<Form.Group className="mb-4" controlId="confirmPassword">
								<Form.Label>
									<i className="bi bi-lock-check-fill me-2 text-muted"></i>
									Confirm Password
								</Form.Label>
								<Form.Control
									type="password"
									name="confirm-password"
									placeholder="Confirm your password"
									value={confirmPassword}
									onChange={(e) => setConfirmPassword(e.target.value)}
									size="lg"
									isInvalid={!!fieldErrors.confirmPassword}
									tabIndex={isLogin ? -1 : 0} // Prevent tab focus when hidden
									autoComplete="new-password"
								/>
								{fieldErrors.confirmPassword && (
									<div className="invalid-feedback">
										{fieldErrors.confirmPassword}
									</div>
								)}
							</Form.Group>
						</div>

						{/* Terms and Conditions checkbox - only for registration */}
						<div className={`auth-field-container ${!isLogin ? 'auth-field-visible' : 'auth-field-hidden'}`}>
							<Form.Group className="mb-4" controlId="terms">
								<Form.Check
									type="checkbox"
									id="acceptTerms"
									name="terms"
									checked={acceptedTerms}
									onChange={(e) => setAcceptedTerms(e.target.checked)}
									isInvalid={!!fieldErrors.terms}
									tabIndex={isLogin ? -1 : 0}
									label={
										<span>
											I agree to the{" "}
											<button
												type="button"
												onClick={(e) => {
													e.preventDefault();
													setShowTerms(true);
												}}
												className="btn-link text-decoration-none fw-semibold text-primary p-0 border-0 bg-transparent"
												style={{ cursor: 'pointer' }}
											>
												Terms and Conditions
											</button>
										</span>
									}
								/>
								{fieldErrors.terms && (
									<div className="invalid-feedback d-block">
										{fieldErrors.terms}
									</div>
								)}
							</Form.Group>
						</div>

						<div className="d-grid">
							<Button
								variant="primary"
								type="submit"
								disabled={loading}
								size="lg"
								className="fw-semibold"
							>
								{loading ? (
									<>
										<Spinner
											as="span"
											animation="border"
											size="sm"
											role="status"
											aria-hidden="true"
											className="me-2"
										/>
										{isLogin ? "Logging in..." : "Creating Account..."}
									</>
								) : (
									<>
										<i className={`bi ${isLogin ? "bi-box-arrow-in-right" : "bi-person-plus"} me-2`}></i>
										{isLogin ? "Login" : "Create Account"}
									</>
								)}
							</Button>
						</div>
					</Form>

					<Card.Footer className="bg-transparent border-top-0 text-center">
						<small className="text-muted">
							{isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
							<button
								type="button"
								onClick={switchMode}
								className="btn-link text-decoration-none fw-semibold text-primary p-0 border-0 bg-transparent"
								style={{ cursor: 'pointer' }}
							>
								{isLogin ? "Create one here" : "Login here"}
							</button>
						</small>
					</Card.Footer>
				</Card.Body>
			</Card>

			{/* Terms and Conditions Modal */}
			<TermsAndConditions
				show={showTerms}
				onHide={() => setShowTerms(false)}
			/>
		</div>
	);
}

export default AuthForm;