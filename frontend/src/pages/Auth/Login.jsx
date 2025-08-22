import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import "./Login.css";
import { ReactComponent as JamLogo } from "../../assets/Logo.svg";
import { Card, Form, Spinner } from "react-bootstrap";
import TermsAndConditions from "./TermsConditions";
import { ActionButton, renderInputField } from "../../components/rendering/form/WidgetRenders";
import { useGlobalToast } from "../../hooks/useNotificationToast";

function AuthForm() {
	const [isLogin, setIsLogin] = useState(true);
	const [formData, setFormData] = useState({
		email: "",
		password: "",
		confirmPassword: "",
	});
	const [acceptedTerms, setAcceptedTerms] = useState(false);
	const [showTerms, setShowTerms] = useState(false);
	const [loading, setLoading] = useState(false);
	const [fieldErrors, setFieldErrors] = useState({});
	const { login, register, isAuthenticated } = useAuth();
	const navigate = useNavigate();
	const location = useLocation();
	const { showSuccess, showError } = useGlobalToast();
	const MIN_PASSWORD_LENGTH = parseInt(process.env.REACT_APP_MIN_PASSWORD_LENGTH);

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

	const handleInputChange = (e) => {
		const { name, value } = e.target;
		setFormData((prev) => ({
			...prev,
			[name]: value,
		}));

		// Clear field errors when user starts typing
		if (fieldErrors[name]) {
			setFieldErrors((prev) => ({
				...prev,
				[name]: "",
			}));
		}
	};

	const switchMode = () => {
		setIsLogin(!isLogin);
		setFieldErrors({});
		// Clear confirm password and terms when switching to login
		if (!isLogin) {
			// noinspection JSCheckFunctionSignatures
			setFormData((prev) => ({
				...prev,
				confirmPassword: "",
			}));
			setAcceptedTerms(false);
		}
		// Update URL without navigation
		window.history.replaceState(null, "", isLogin ? "/register" : "/login");
	};

	const resetForm = () => {
		setFormData({
			email: "",
			password: "",
			confirmPassword: "",
		});
		setAcceptedTerms(false);
		setFieldErrors({});
	};

	const validateForm = () => {
		const errors = {};

		// Email validation
		if (!formData.email || !formData.email.includes("@")) {
			errors.email = "Please provide a valid email address.";
		}

		// Password validation
		if (!formData.password) {
			errors.password = "Password is required.";
		} else if (!isLogin && formData.password.length < MIN_PASSWORD_LENGTH) {
			errors.password = `Password must be at least ${MIN_PASSWORD_LENGTH} characters long.`;
		}

		// Confirm password validation (only for register)
		if (!isLogin) {
			if (!formData.confirmPassword) {
				errors.confirmPassword = "Please confirm your password.";
			} else if (formData.password !== formData.confirmPassword) {
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

		setLoading(true);

		try {
			if (isLogin) {
				const result = await login(formData.email, formData.password);
				if (result.success) {
					navigate("/dashboard");
				} else {
					if ([404, 403].includes(result.status)) {
						showError("Incorrect email or password", "Login Failed");
					} else {
						showError("Failed to login. An unknown error occurred", "Login Failed");
					}
				}
			} else {
				const result = await register(formData.email, formData.password);
				console.log(result);
				if (result.success) {
					setIsLogin(true);
					resetForm();
					window.history.replaceState(null, "", "/login");
					showSuccess("Account created successfully! You can now log in.", "Registration Successful");
				} else if (result.status === 400) {
					showError("Email already registered", "Registration Failed");
				} else {
					const errorMessage =
						typeof result.error === "object"
							? JSON.stringify(result.error)
							: result.error || "Registration failed";
					showError(errorMessage, "Registration Error");
				}
			}
		} catch (error) {
			showError(
				isLogin
					? "Failed to login. An unknown error occurred"
					: "Failed to create an account. An unknown error occurred",
				isLogin ? "Login Error" : "Registration Error",
			);
		}

		setLoading(false);
	}

	// Define field configurations
	const emailField = {
		name: "email",
		type: "text",
		placeholder: "Enter your email",
	};

	const passwordField = {
		name: "password",
		type: "password",
		placeholder: "Enter your password",
		autoComplete: isLogin ? "current-password" : "new-password",
		helpText: !isLogin ? "Password must be at least 8 characters long" : null,
	};

	const confirmPasswordField = {
		name: "confirmPassword",
		type: "password",
		placeholder: "Confirm your password",
		autoComplete: "new-password",
		tabIndex: isLogin ? -1 : 0,
	};

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
					<div className="logo-text-below text-gradient-primary" style={{ fontSize: "50px" }}>
						Job Application Manager
					</div>
				</div>
			</div>

			<Card className="auth-card border-0 auth-card-animated">
				<Card.Body>
					<Card.Title className="text-primary">{isLogin ? "Login" : "Create Account"}</Card.Title>

					<Form onSubmit={handleSubmit} autoComplete="on">
						<Form.Group className="mb-3">
							<Form.Label>
								<i className="bi bi-envelope-fill me-2 text-muted"></i>
								Email Address
							</Form.Label>
							{renderInputField(emailField, formData, handleInputChange, fieldErrors)}
						</Form.Group>

						<Form.Group className="mb-3">
							<Form.Label>
								<i className="bi bi-lock-fill me-2 text-muted"></i>
								Password
							</Form.Label>
							{renderInputField(passwordField, formData, handleInputChange, fieldErrors)}
						</Form.Group>

						{/* Always render confirm password field but control visibility with CSS */}
						<div
							className={`auth-field-container ${!isLogin ? "auth-field-visible" : "auth-field-hidden"}`}
						>
							<Form.Group className="mb-4">
								<Form.Label>
									<i className="bi bi-lock-check-fill me-2 text-muted"></i>
									Confirm Password
								</Form.Label>
								{renderInputField(confirmPasswordField, formData, handleInputChange, fieldErrors)}
							</Form.Group>
						</div>

						{/* Terms and Conditions checkbox - only for registration */}
						<div
							className={`auth-field-container ${!isLogin ? "auth-field-visible" : "auth-field-hidden"}`}
						>
							<Form.Group className="mb-4">
								<Form.Check
									type="checkbox"
									id="accept-terms"
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
												style={{ cursor: "pointer" }}
											>
												Terms and Conditions
											</button>
										</span>
									}
								/>
								{fieldErrors.terms && (
									<div id="terms-error-message" className="invalid-feedback d-block">
										{fieldErrors.terms}
									</div>
								)}
							</Form.Group>
						</div>

						<div className="d-grid">
							<ActionButton
								id="confirm-button"
								type="submit"
								disabled={loading}
								loading={loading}
								className="fw-semibold"
								loadingText={isLogin ? "Logging in..." : "Creating Account..."}
								defaultText={isLogin ? "Login" : "Create Account"}
								defaultIcon={isLogin ? "bi bi-box-arrow-in-right" : "bi bi-person-plus"}
							/>
						</div>
					</Form>

					<Card.Footer className="bg-transparent border-top-0 text-center">
						<small className="text-muted">
							{isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
							<button
								type="button"
								id="switch-mode-button"
								onClick={switchMode}
								className="btn-link text-decoration-none fw-semibold text-primary p-0 border-0 bg-transparent"
								style={{ cursor: "pointer" }}
							>
								{isLogin ? "Create one here" : "Login here"}
							</button>
						</small>
					</Card.Footer>
				</Card.Body>
			</Card>

			<TermsAndConditions show={showTerms} onHide={() => setShowTerms(false)} />
		</div>
	);
}

export default AuthForm;
