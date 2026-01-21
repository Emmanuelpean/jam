import React, { JSX, useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { FormData, useAuth } from "../../contexts/AuthContext";
import "./AuthPage.css";
import { ReactComponent as JamLogo } from "../../assets/Logo.svg";
import { Alert, Card, Form, Spinner } from "react-bootstrap";
import TermsAndConditions from "./TermsConditions";
import { Errors, rendFormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { authApi, GenericResponse } from "../../services/api/Users";
import { ApiError, ApiResponse } from "../../services/api/Base";
import { useLoading } from "../../contexts/LoadingContext";
import { DEFAULT_THEME } from "../../utils/Theme";

type AuthMode = "login" | "register" | "forgotPassword" | "resetPassword" | "verifyEmail" | "verifyNewEmail";

let isVerifying: boolean = false;

const determineAuthMode = (pathname: string, token: string | null): AuthMode => {
	const normalizedPath: string = pathname.endsWith("/") && pathname.length > 1 ? pathname.slice(0, -1) : pathname;

	if (normalizedPath === "/reset-password" && token) return "resetPassword";
	if (normalizedPath === "/verify-email") return "verifyEmail";
	if (normalizedPath === "/verify-new-email") return "verifyNewEmail";
	if (normalizedPath === "/forgot-password") return "forgotPassword";
	if (normalizedPath === "/register") return "register";
	return "login";
};

const defaultFormData: FormData = {
	email: "",
	password: "",
	confirmPassword: "",
	firstName: "",
	lastName: "",
};

function AuthForm(): JSX.Element {
	const location = useLocation();
	const navigate = useNavigate();
	const [searchParams, setSearchParams] = useSearchParams();
	const [mode, setMode] = useState<AuthMode>(() => determineAuthMode(location.pathname, searchParams.get("token")));
	const [registrationStep, setRegistrationStep] = useState<number>(1);
	const [formData, setFormData] = useState<FormData>(defaultFormData);
	const [resetToken, setResetToken] = useState<string>("");
	const [showTestInfo, setShowTestInfo] = useState(false);
	const [showMobileWarning, setShowMobileWarning] = useState<boolean>(false);
	const [acceptedTerms, setAcceptedTerms] = useState<boolean>(false);
	const [showTerms, setShowTerms] = useState<boolean>(false);
	const [loading, setLoading] = useState<boolean>(false);
	const [fieldErrors, setFieldErrors] = useState<Errors>({});
	const { logout, login, isAuthenticated } = useAuth();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const MIN_PASSWORD_LENGTH = parseInt(process.env.REACT_APP_MIN_PASSWORD_LENGTH || "8");
	const { showLoading, hideLoading } = useLoading();
	const contentRef = useRef<HTMLDivElement>(null);
	const [contentHeight, setContentHeight] = useState<number | "auto">("auto");

	useEffect(() => {
		if (contentRef.current) {
			setContentHeight(contentRef.current.scrollHeight);
		}
	}, [mode, registrationStep, fieldErrors]);
	document.documentElement.setAttribute("data-theme", DEFAULT_THEME);

	useEffect(() => {
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
		if (!["verifyEmail", "verifyNewEmail"].includes(mode) || isVerifying) return;

		const verifyToken: string | null = searchParams.get("token");

		let api = null;
		if (mode === "verifyEmail") {
			api = authApi.verifyEmail;
		} else if (mode === "verifyNewEmail") {
			api = authApi.verifyNewEmail;
		}

		if (!verifyToken || !api) return;

		isVerifying = true;
		if (isAuthenticated) {
			logout();
		}
		showLoading("Verifying email...", undefined);

		api(verifyToken)
			.then((response: ApiResponse<GenericResponse>) => {
				showToastSuccess(response.data.message, "Email Verified");
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
			})
		);

		if (fieldErrors[name as keyof Errors]) {
			setFieldErrors((prev: Errors) => ({
				...prev,
				[name]: "",
			}));
		}
	};

	const resetForm = (): void => {
		setFormData(defaultFormData);
		setAcceptedTerms(false);
		setFieldErrors({});
		setResetToken("");
		setRegistrationStep(1);
	};

	const switchToRegister = (): void => {
		setSearchParams({});
		setMode("register");
		setRegistrationStep(1);
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
		navigate("/login");
		resetForm();
	};

	const validateForm = (currentStep?: number): Errors => {
		const errors: Errors = {};

		if (mode === "register") {
			const step = currentStep ?? registrationStep;

			if (step === 1) {
				if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
					errors.email = "Please provide a valid email address.";
				}

				if (!formData.password) {
					errors.password = "Password is required.";
				} else if (formData.password.length < MIN_PASSWORD_LENGTH) {
					errors.password = `Password must be at least ${MIN_PASSWORD_LENGTH} characters long.`;
				}

				if (!formData.confirmPassword) {
					errors.confirmPassword = "Please confirm your password.";
				} else if (formData.password !== formData.confirmPassword) {
					errors.confirmPassword = "Passwords do not match.";
				}

				if (!acceptedTerms) {
					errors.terms = "You must accept the Terms and Conditions to register.";
				}
			} else if (step === 2) {
				if (!formData.firstName || formData.firstName.trim().length === 0) {
					errors.firstName = "First name is required.";
				}

				if (!formData.lastName || formData.lastName.trim().length === 0) {
					errors.lastName = "Last name is required.";
				}
			}

			return errors;
		}

		if (["login", "forgotPassword"].includes(mode)) {
			if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
				errors.email = "Please provide a valid email address.";
			}
		}

		if (["login", "resetPassword"].includes(mode)) {
			if (!formData.password) {
				errors.password = "Password is required.";
			} else if (["resetPassword"].includes(mode) && formData.password.length < MIN_PASSWORD_LENGTH) {
				errors.password = `Password must be at least ${MIN_PASSWORD_LENGTH} characters long.`;
			}

			if (["resetPassword"].includes(mode)) {
				if (!formData.confirmPassword) {
					errors.confirmPassword = "Please confirm your password.";
				} else if (formData.password !== formData.confirmPassword) {
					errors.confirmPassword = "Passwords do not match.";
				}
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
			const result: GenericResponse = await login(formData.email, formData.password);

			if (result.success) {
				navigate("/dashboard");
			} else {
				showToastError(result.message, "Login Failed");
			}
		} catch (error) {
			const apiError = error as ApiError;
			showToastError(apiError.message || "Failed to login. An unknown error occurred", "Login Failed");
		} finally {
			setLoading(false);
		}
	};

	const handleNextStep = (): void => {
		const errors: Errors = validateForm(registrationStep);
		setFieldErrors(errors);

		if (Object.keys(errors).length > 0) {
			return;
		}

		setRegistrationStep(2);
	};

	const handlePreviousStep = (): void => {
		setRegistrationStep(1);
		setFieldErrors({});
	};

	const handleRegister = async (): Promise<void> => {
		const errors: Errors = validateForm(registrationStep);
		setFieldErrors(errors);

		if (Object.keys(errors).length > 0) {
			return;
		}

		setLoading(true);

		try {
			const result: ApiResponse<GenericResponse> = await authApi.register({
				email: formData.email,
				password: formData.password,
				first_name: formData.firstName,
				last_name: formData.lastName,
			});

			if (result.data.success) {
				switchToLogin();
				showToastSuccess(
					"Account created! Please check your email to verify your account before logging in.",
					"Registration Successful"
				);
			} else {
				showToastError(result.data.message, "Registration Failed");
			}
		} catch (error) {
			const apiError = error as ApiError;
			showToastError(
				apiError.message || "Failed to create an account. An unknown error occurred",
				"Registration Failed"
			);
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
			const response: ApiResponse = await authApi.requestPasswordReset(formData.email);
			showToastSuccess(response.data.message, "Reset Link Sent");
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
			const response: ApiResponse = await authApi.resetPassword(resetToken, formData.password);
			showToastSuccess(response.data.message, "Password Reset Successful");
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
		} else if (mode === "register") {
			if (registrationStep === 1) {
				handleNextStep();
			} else {
				handleRegister().then(() => {});
			}
		}
	};

	const handleTermsCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
		setAcceptedTerms(e.target.checked);
	};

	const handleShowTerms = (e: React.MouseEvent<HTMLButtonElement>): void => {
		e.preventDefault();
		setShowTerms(true);
	};

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
	};

	const firstNameField: ModalFormField = {
		name: "firstName",
		type: "text",
		label: "First Name",
		icon: "bi bi-person-fill",
		placeholder: "Enter your first name",
	};

	const lastNameField: ModalFormField = {
		name: "lastName",
		type: "text",
		label: "Last Name",
		icon: "bi bi-person-fill",
		placeholder: "Enter your last name",
	};

	const cardTitle: string =
		mode === "resetPassword"
			? "Set New Password"
			: mode === "forgotPassword"
				? "Reset Your Password"
				: mode === "login"
					? "Login"
					: registrationStep === 1
						? "Create Account"
						: "Personal Information";

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

	const handleDemoLogin = async (): Promise<void> => {
		setLoading(true);
		try {
			const result: GenericResponse = await login("test_user@test.com", "test_password");
			if (result.success) {
				navigate("/dashboard");
			} else {
				showToastError(result.message, "Login Failed");
			}
		} catch (error) {
			const apiError = error as ApiError;
			showToastError(apiError.message || "Failed to login with demo account.", "Demo Login Failed");
		} finally {
			setLoading(false);
			setShowTestInfo(false);
		}
	};

	return (
		<div className="auth-container">
			<div className="floating-demo-info">
				<button
					className="demo-info-trigger"
					onClick={() => setShowTestInfo(!showTestInfo)}
					aria-label="Demo account"
					disabled={loading}
				>
					<i className={`bi bi-backpack3`} style={{ fontSize: "20px" }}></i>
					<span className="demo-text">Try Demo</span>
				</button>
				{showTestInfo && (
					<>
						<div className="demo-backdrop" onClick={() => setShowTestInfo(false)} />
						<div className="demo-info-panel">
							<button
								className="demo-close-btn"
								onClick={() => setShowTestInfo(false)}
								aria-label="Close"
							>
								✕
							</button>
							<h3 className="demo-title">Welcome to JAM</h3>
							<p className="demo-welcome">
								You can try the app using a demo account with pre-populated data.
							</p>
							<ActionButton
								className="demo-login-btn"
								onClick={handleDemoLogin}
								loading={loading}
								defaultText={"Login with Demo Account"}
								loadingText={"Logging in..."}
								defaultIcon={"bi bi-box-arrow-in-right"}
							/>
							<p className="demo-note">
								<small className="text-muted">
									This is a test account with sample job applications and data.
								</small>
							</p>
						</div>
					</>
				)}
			</div>
			<div className="auth-logo">
				<div className="logo-container logo-container-vertical">
					<JamLogo style={{ height: "175px", width: "auto", userSelect: "none" }} />
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

			<Card className="auth-card border-0" style={{ height: contentHeight }}>
				<div ref={contentRef} style={{ padding: "2.5rem" }}>
					<Card.Body>
						<Card.Title className="text-primary">{cardTitle}</Card.Title>

						{mode === "register" && (
							<div className="mb-3">
								<div className="d-flex justify-content-between align-items-center mb-2">
									<small className="text-muted">Step {registrationStep} of 2</small>
								</div>
								<div className="progress" style={{ height: "4px" }}>
									<div
										className="progress-bar"
										role="progressbar"
										style={{ width: `${(registrationStep / 2) * 100}%` }}
										aria-valuenow={(registrationStep / 2) * 100}
										aria-valuemin={0}
										aria-valuemax={100}
									></div>
								</div>
							</div>
						)}

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
							{/* Registration Step 1 */}
							{mode === "register" && registrationStep === 1 && (
								<>
									{rendFormField(emailField, formData, handleInputChange, fieldErrors)}
									{rendFormField(passwordField, formData, handleInputChange, fieldErrors)}
									{rendFormField(confirmPasswordField, formData, handleInputChange, fieldErrors)}
									{rendFormField(
										termsField,
										{ terms: acceptedTerms },
										//@ts-ignore
										handleTermsCheckboxChange,
										fieldErrors
									)}
								</>
							)}

							{/* Registration Step 2 */}
							{mode === "register" && registrationStep === 2 && (
								<>
									{rendFormField(firstNameField, formData, handleInputChange, fieldErrors)}
									{rendFormField(lastNameField, formData, handleInputChange, fieldErrors)}
								</>
							)}

							{/* Login Mode */}
							{mode === "login" && (
								<>
									{rendFormField(emailField, formData, handleInputChange, fieldErrors)}
									{rendFormField(passwordField, formData, handleInputChange, fieldErrors)}
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
								</>
							)}

							{/* Forgot Password Mode */}
							{mode === "forgotPassword" && (
								<>{rendFormField(emailField, formData, handleInputChange, fieldErrors)}</>
							)}

							{/* Reset Password Mode */}
							{mode === "resetPassword" && (
								<>
									{rendFormField(passwordField, formData, handleInputChange, fieldErrors)}
									{rendFormField(confirmPasswordField, formData, handleInputChange, fieldErrors)}
								</>
							)}

							{/* Action buttons */}
							<div className="d-grid gap-2">
								{mode === "register" && registrationStep === 2 && (
									<ActionButton
										type="button"
										onClick={handlePreviousStep}
										variant="secondary"
										className="fw-semibold"
										defaultText="Back"
										defaultIcon="bi bi-arrow-left"
									/>
								)}

								<ActionButton
									type="submit"
									id="confirm-button"
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
													: registrationStep === 1
														? "Next..."
														: "Creating Account..."
									}
									defaultText={
										mode === "resetPassword"
											? "Reset Password"
											: mode === "forgotPassword"
												? "Send Reset Link"
												: mode === "login"
													? "Login"
													: registrationStep === 1
														? "Next"
														: "Create Account"
									}
									defaultIcon={
										mode === "resetPassword"
											? "bi bi-shield-lock"
											: mode === "forgotPassword"
												? "bi bi-envelope-paper"
												: mode === "login"
													? "bi bi-box-arrow-in-right"
													: registrationStep === 1
														? "bi bi-arrow-right"
														: "bi bi-person-plus"
									}
								/>
							</div>
						</Form>

						<Card.Footer className="bg-transparent border-0 text-center">
							<small className="text-muted">
								{mode === "resetPassword" || mode === "forgotPassword" ? (
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
				</div>
			</Card>

			<TermsAndConditions show={showTerms} onHide={() => setShowTerms(false)} />
		</div>
	);
}

export default AuthForm;
