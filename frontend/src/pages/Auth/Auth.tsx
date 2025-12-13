import React, { JSX, useEffect, useState } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { AuthResponse, FormData, useAuth } from "../../contexts/AuthContext";
import "./Auth.css";
import { ReactComponent as JamLogo } from "../../assets/Logo.svg";
import { Alert, Card, Form, Spinner } from "react-bootstrap";
import TermsAndConditions from "./TermsConditions";
import { Errors, FormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { authApi } from "../../services/api/Users";
import { ApiError } from "../../services/api/Base";
import { useLoading } from "../../contexts/LoadingContext";

interface VerificationResponse {
	message: string;
}

type AuthMode = "login" | "register" | "forgotPassword" | "resetPassword" | "verifyEmail" | "verifyNewEmail";

let isVerifying = false;

const determineAuthMode = (pathname: string, token: string | null): AuthMode => {
	// Remove trailing slash for consistent comparison
	const normalizedPath = pathname.endsWith("/") && pathname.length > 1 ? pathname.slice(0, -1) : pathname;

	if (normalizedPath === "/reset-password" && token) return "resetPassword";
	if (normalizedPath === "/verify-email") return "verifyEmail";
	if (normalizedPath === "/verify-new-email") return "verifyNewEmail";
	if (normalizedPath === "/forgot-password") return "forgotPassword";
	if (normalizedPath === "/register") return "register";
	return "login";
};

function AuthForm(): JSX.Element {
	const location = useLocation();
	const navigate = useNavigate();
	const [searchParams, setSearchParams] = useSearchParams();
	const [mode, setMode] = useState<AuthMode>(() => determineAuthMode(location.pathname, searchParams.get("token")));
	const [formData, setFormData] = useState<FormData>({
		email: "",
		password: "",
		confirmPassword: "",
	});
	const [resetToken, setResetToken] = useState<string>("");
	const [showBanner, setShowBanner] = useState<boolean>(true);
	const [showMobileWarning, setShowMobileWarning] = useState<boolean>(false);
	const [acceptedTerms, setAcceptedTerms] = useState<boolean>(false);
	const [showTerms, setShowTerms] = useState<boolean>(false);
	const [loading, setLoading] = useState<boolean>(false);
	const [fieldErrors, setFieldErrors] = useState<Errors>({});
	const { logout, login, register, isAuthenticated } = useAuth();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const MIN_PASSWORD_LENGTH = parseInt(process.env.REACT_APP_MIN_PASSWORD_LENGTH || "8");
	const { showLoading, hideLoading } = useLoading();

	document.documentElement.setAttribute("data-theme", "mixed-berry");

	useEffect(() => {
		// Update mode based on URL path and query params and redirect if authenticated
		const token = searchParams.get("token");
		const newMode = determineAuthMode(location.pathname, token);

		if (newMode === "resetPassword" && token) {
			setResetToken(token);
		}

		setMode(newMode);

		if (isAuthenticated && (newMode === "login" || newMode === "register")) {
			navigate("/dashboard", { replace: true });
		}
	}, [location.pathname, isAuthenticated, searchParams, navigate]);

	useEffect(() => {
		// Verifies the email
		if (!["verifyEmail", "verifyNewEmail"].includes(mode) || isVerifying) return;

		const verifyToken: string | null = searchParams.get("token");

		let api = null;
		if (mode == "verifyEmail") {
			api = authApi.verifyEmail;
		} else if (mode == "verifyNewEmail") {
			api = authApi.verifyNewEmail;
		}

		if (!verifyToken || !api) return;

		isVerifying = true;
		if (isAuthenticated) {
			logout();
		}
		showLoading("Verifying email...", undefined);

		api(verifyToken)
			.then((response: VerificationResponse) => {
				showToastSuccess(response.message, "Email Verified");
				setSearchParams({});
			})
			.catch((err: any) => {
				const apiError = err as ApiError;
				showToastError(apiError.message, "Verification Failed");
				setSearchParams({});
			})
			.finally(() => {
				hideLoading();
				setTimeout(() => {
					isVerifying = false;
				}, 1000);
				switchToLogin();
			});
	}, [mode, location.pathname, searchParams, navigate]);

	// Detect small screens
	useEffect(() => {
		const checkScreenSize = () => {
			setShowMobileWarning(window.innerWidth < 768);
		};

		checkScreenSize();
		window.addEventListener("resize", checkScreenSize);
		return () => window.removeEventListener("resize", checkScreenSize);
	}, []);

	const handleInputChange = (e: SyntheticEvent): void => {
		const { name, value } = e.target;
		setFormData(
			(prev: FormData): FormData => ({
				...prev,
				[name]: value,
			}),
		);

		if (fieldErrors[name as keyof Errors]) {
			setFieldErrors((prev: Errors) => ({
				...prev,
				[name]: "",
			}));
		}
	};

	const resetForm = (): void => {
		setFormData({
			email: "",
			password: "",
			confirmPassword: "",
		});
		setAcceptedTerms(false);
		setFieldErrors({});
		setResetToken("");
	};

	const switchToRegister = (): void => {
		setSearchParams({});
		setMode("register");
		resetForm();
		navigate("/register");
	};

	const switchToForgotPassword = (): void => {
		setSearchParams({});
		setMode("forgotPassword");
		resetForm();
		navigate("/forgot-password");
	};

	const switchToLogin = (): void => {
		setSearchParams({});
		// setMode("login");

		navigate("/login");
		resetForm();
	};

	const validateForm = (): Errors => {
		const errors: Errors = {};

		// Email validation
		if (["login", "register", "forgotPassword"].includes(mode)) {
			if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
				errors.email = "Please provide a valid email address.";
			}
		}

		// Password validation
		if (["login", "register", "resetPassword"].includes(mode)) {
			if (!formData.password) {
				errors.password = "Password is required.";
			} else if (["register", "resetPassword"].includes(mode) && formData.password.length < MIN_PASSWORD_LENGTH) {
				errors.password = `Password must be at least ${MIN_PASSWORD_LENGTH} characters long.`;
			}

			// Confirm password validation (for register and resetPassword)
			if (["register", "resetPassword"].includes(mode)) {
				if (!formData.confirmPassword) {
					errors.confirmPassword = "Please confirm your password.";
				} else if (formData.password !== formData.confirmPassword) {
					errors.confirmPassword = "Passwords do not match.";
				}
			}

			// Terms acceptance validation (only for register)
			if (mode === "register" && !acceptedTerms) {
				errors.terms = "You must accept the Terms and Conditions to register.";
			}
		}

		return errors;
	};

	const handleLogin = async (): Promise<void> => {
		const errors: Errors = validateForm();
		setFieldErrors(errors);

		if (Object.keys(errors).length > 0) {
			return;
		}

		setLoading(true);

		try {
			const result: AuthResponse = await login(formData.email, formData.password);

			if (result.success) {
				navigate("/dashboard");
			} else {
				showToastError(result.error!, "Login Failed");
			}
		} catch (error) {
			showToastError("Failed to login. An unknown error occurred", "Login Failed");
		} finally {
			setLoading(false);
		}
	};

	const handleRegister = async (): Promise<void> => {
		const errors: Errors = validateForm();
		setFieldErrors(errors);

		if (Object.keys(errors).length > 0) {
			return;
		}

		setLoading(true);

		try {
			const result: AuthResponse = await register(formData.email, formData.password);

			if (result.success) {
				switchToLogin();
				showToastSuccess(
					"Account created! Please check your email to verify your account before logging in.",
					"Registration Successful",
				);
			} else {
				showToastError(result.error!, "Registration Failed");
			}
		} catch (error) {
			showToastError("Failed to create an account. An unknown error occurred", "Registration Failed");
		} finally {
			setLoading(false);
		}
	};

	const handleForgotPassword = async (): Promise<void> => {
		const errors = validateForm();
		setFieldErrors(errors);

		if (Object.keys(errors).length > 0) {
			return;
		}

		setLoading(true);

		try {
			const response = await authApi.requestPasswordReset(formData.email);
			showToastSuccess(response.message, "Reset Link Sent");
		} catch (error) {
			const apiError = error as ApiError;
			showToastError(apiError.message, "Error Sending Reset Link");
		} finally {
			setLoading(false);
		}
	};

	const handleResetPassword = async (): Promise<void> => {
		const errors = validateForm();
		setFieldErrors(errors);

		if (Object.keys(errors).length > 0) {
			return;
		}

		setLoading(true);

		try {
			const response = await authApi.resetPassword(resetToken, formData.password);
			showToastSuccess(response.message, "Password Reset Successful");
			switchToLogin();
		} catch (error) {
			const apiError = error as ApiError;
			showToastError(apiError.message, "Reset Failed");
		} finally {
			setLoading(false);
		}
	};

	const handleSubmit = (e: React.FormEvent<HTMLFormElement>): void => {
		e.preventDefault();

		if (mode === "resetPassword") {
			handleResetPassword().then(() => {});
		} else if (mode === "forgotPassword") {
			handleForgotPassword().then(() => {});
		} else if (mode === "login") {
			handleLogin().then(() => {});
		} else {
			handleRegister().then(() => {});
		}
	};

	const handleTermsCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
		setAcceptedTerms(e.target.checked);
	};

	const handleShowTerms = (e: React.MouseEvent<HTMLButtonElement>): void => {
		e.preventDefault();
		setShowTerms(true);
	};

	// Define field configurations
	const emailField: ModalFormField = {
		name: "email",
		type: "text",
		label: "Email Address",
		icon: "bi bi-envelope-fill",
		placeholder: "Enter your email",
	};

	const passwordField: ModalFormField = {
		name: "password",
		type: "password",
		label: mode === "resetPassword" ? "New Password" : "Password",
		icon: "bi bi-lock-fill",
		placeholder: mode === "resetPassword" ? "Enter your new password" : "Enter your password",
		autoComplete: mode === "login" ? "current-password" : "new-password",
		helpText: ["register", "resetPassword"].includes(mode)
			? `Password must be at least ${MIN_PASSWORD_LENGTH} characters long`
			: null,
	};

	const confirmPasswordField: ModalFormField = {
		name: "confirmPassword",
		type: "password",
		label: "Confirm Password",
		icon: "bi bi-lock-fill",
		placeholder: mode === "resetPassword" ? "Confirm your new password" : "Confirm your password",
		autoComplete: "new-password",
		tabIndex: mode === "login" ? -1 : 0,
	};

	const cardTitle: string =
		mode === "resetPassword"
			? "Set New Password"
			: mode === "forgotPassword"
				? "Reset Your Password"
				: mode === "login"
					? "Login"
					: "Create Account";

	const termsField: ModalFormField = {
		name: "terms",
		type: "checkbox",
		label: (
			<span>
				I agree to the{" "}
				<button
					type="button"
					onClick={handleShowTerms}
					className="btn-link text-decoration-none fw-semibold text-primary p-0 border-0 bg-transparent"
					style={{ cursor: "pointer" }}
				>
					Terms and Conditions
				</button>
			</span>
		),
	};

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
					<JamLogo style={{ height: "175px", width: "auto" }} />
					<div className="logo-text-below text-gradient-primary" style={{ fontSize: "50px" }}>
						Job Application Manager
					</div>
				</div>
			</div>

			{showMobileWarning && (
				<Alert
					variant="warning"
					dismissible
					onClose={() => setShowMobileWarning(false)}
					className="mb-3"
					style={{ maxWidth: "500px" }}
				>
					<Alert.Heading className="h6 d-flex align-items-center mb-2">
						<i className="bi bi-exclamation-triangle-fill me-2"></i>
						Limited Mobile Support
					</Alert.Heading>
					<p className="mb-0 small">
						JAM is not fully optimised for small screens yet. For the best experience, please use a tablet
						or desktop device.
					</p>
				</Alert>
			)}

			{mode === "login" && showBanner && (
				<Alert
					variant="info"
					dismissible
					onClose={() => setShowBanner(false)}
					className="mb-3"
					style={{ maxWidth: "500px" }}
				>
					<Alert.Heading className="h6 d-flex align-items-center mb-2">
						<i className="bi bi-rocket-takeoff-fill me-2"></i>
						Welcome to JAM Early Alpha!
					</Alert.Heading>
					<p className="mb-2 small">Thanks for testing! Try out the app with these demo credentials:</p>
					<div className="d-flex flex-column gap-1 mb-2" style={{ fontSize: "0.875rem" }}>
						<div>
							<strong>Email:</strong>{" "}
							<code className="bg-light px-2 py-1 rounded">test_user@test.com</code>
						</div>
						<div>
							<strong>Password:</strong> <code className="bg-light px-2 py-1 rounded">test_password</code>
						</div>
					</div>
					<p className="mb-0 small text-muted">
						Found a bug or have feedback?{" "}
						<a
							href="mailto:jam.support@emmanuelpean.me?subject=JAM Feedback"
							className="text-decoration-none fw-semibold"
						>
							Let me know!
						</a>
					</p>
				</Alert>
			)}

			<Card className="auth-card border-0 auth-card-animated">
				<Card.Body>
					<Card.Title className="text-primary">{cardTitle}</Card.Title>

					{mode === "forgotPassword" && (
						<p className="text-muted mb-4">
							Enter your email address and we'll send you a link to reset your password.
						</p>
					)}

					{mode === "resetPassword" && (
						<p className="text-muted mb-4">
							Please enter your new password below. Make sure it's strong and secure.
						</p>
					)}

					<Form onSubmit={handleSubmit} autoComplete="on">
						{/* Email field - visible for login, register, and forgotPassword */}
						<div
							className={`auth-field-container ${mode !== "resetPassword" ? "auth-field-visible" : "auth-field-hidden"}`}
						>
							{FormField(emailField, formData, handleInputChange, fieldErrors)}
						</div>

						{/* Password field - visible for login, register, and resetPassword */}
						<div
							className={`auth-field-container ${mode !== "forgotPassword" ? "auth-field-visible" : "auth-field-hidden"}`}
						>
							{FormField(passwordField, formData, handleInputChange, fieldErrors)}
						</div>

						{/* Forgot password link - visible only for login */}
						<div
							className={`auth-field-container ${mode === "login" ? "auth-field-visible" : "auth-field-hidden"}`}
						>
							<div className="text-end mb-3">
								<button
									type="button"
									onClick={switchToForgotPassword}
									className="btn-link text-decoration-none fw-semibold text-primary p-0 border-0 bg-transparent small"
									style={{ cursor: "pointer" }}
									id="forgot-password-link"
								>
									Forgot your password?
								</button>
							</div>
						</div>

						{/* Confirm password - visible for register and resetPassword */}
						<div
							className={`auth-field-container ${["register", "resetPassword"].includes(mode) ? "auth-field-visible" : "auth-field-hidden"}`}
						>
							{FormField(confirmPasswordField, formData, handleInputChange, fieldErrors)}
						</div>

						{/* Terms checkbox - visible only for register */}
						<div
							className={`auth-field-container ${mode === "register" ? "auth-field-visible" : "auth-field-hidden"}`}
						>
							{FormField(
								termsField,
								{ terms: acceptedTerms },
								//@ts-ignore
								handleTermsCheckboxChange,
								fieldErrors,
							)}
						</div>

						<div className="d-grid">
							<ActionButton
								id="confirm-button"
								type="submit"
								disabled={loading}
								loading={loading}
								className="fw-semibold"
								loadingText={
									mode === "resetPassword"
										? "Resetting Password..."
										: mode === "forgotPassword"
											? "Sending..."
											: mode === "login"
												? "Logging in..."
												: "Creating Account..."
								}
								defaultText={
									mode === "resetPassword"
										? "Reset Password"
										: mode === "forgotPassword"
											? "Send Reset Link"
											: mode === "login"
												? "Login"
												: "Create Account"
								}
								defaultIcon={
									mode === "resetPassword"
										? "bi bi-shield-lock"
										: mode === "forgotPassword"
											? "bi bi-envelope-paper"
											: mode === "login"
												? "bi bi-box-arrow-in-right"
												: "bi bi-person-plus"
								}
							/>
						</div>
					</Form>

					<Card.Footer className="bg-transparent border-0 text-center">
						<small className="text-muted">
							{mode === "resetPassword" ? (
								<>
									Remember your password?{" "}
									<button
										type="button"
										onClick={switchToLogin}
										className="btn-link text-decoration-none fw-semibold text-primary p-0 border-0 bg-transparent"
										style={{ cursor: "pointer" }}
									>
										Back to Login
									</button>
								</>
							) : mode === "forgotPassword" ? (
								<>
									Remember your password?{" "}
									<button
										type="button"
										onClick={switchToLogin}
										className="btn-link text-decoration-none fw-semibold text-primary p-0 border-0 bg-transparent"
										style={{ cursor: "pointer" }}
									>
										Back to Login
									</button>
								</>
							) : mode === "login" ? (
								<>
									Don't have an account?{" "}
									<button
										type="button"
										id="switch-mode-button"
										onClick={switchToRegister}
										className="btn-link text-decoration-none fw-semibold text-primary p-0 border-0 bg-transparent"
										style={{ cursor: "pointer" }}
									>
										Create one here
									</button>
								</>
							) : (
								<>
									Already have an account?{" "}
									<button
										type="button"
										id="switch-mode-button"
										onClick={switchToLogin}
										className="btn-link text-decoration-none fw-semibold text-primary p-0 border-0 bg-transparent"
										style={{ cursor: "pointer" }}
									>
										Login here
									</button>
								</>
							)}
						</small>
					</Card.Footer>
				</Card.Body>
			</Card>

			<TermsAndConditions show={showTerms} onHide={() => setShowTerms(false)} />
		</div>
	);
}

export default AuthForm;
