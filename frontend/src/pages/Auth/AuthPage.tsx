import React, { JSX, useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { FormData, useAuth } from "../../contexts/AuthContext";
import "./AuthPage.scss";
import JamLogo from "../../assets/Logo.svg?react";
import { Card, Form, Spinner } from "react-bootstrap";
import TermsAndConditions from "./TermsConditions";
import { PrivacyPolicyModal } from "./PrivacyPolicyPage";
import { Errors, renderFormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { EmailValidation, ModalFormField } from "../../components/rendering/form/FormRenders";
import { authApi, GenericResponse } from "../../services/api/Users";
import { ApiResponse } from "../../services/api/Base";
import { useLoading } from "../../contexts/LoadingContext";
import { DEFAULT_THEME } from "../../utils/Theme";
import { ApiError } from "../../services/api/ApiError";
import { useConfig } from "../../contexts/ConfigContext";
import { useViewport } from "../../contexts/ViewportContext";
import TurnstileWidget from "./TurnstileWidget";

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

interface Feature {
	icon: string;
	text: string;
	description: string;
}

function AuthForm(): JSX.Element {
	const location = useLocation();
	const navigate = useNavigate();
	const { config } = useConfig();
	const [searchParams, setSearchParams] = useSearchParams();
	const [mode, setMode] = useState<AuthMode>(determineAuthMode(location.pathname, searchParams.get("token")));
	const [registrationStep, setRegistrationStep] = useState<number>(1);
	const [formData, setFormData] = useState<FormData>(defaultFormData);
	const [resetToken, setResetToken] = useState<string>("");
	const [acceptedTerms, setAcceptedTerms] = useState<boolean>(false);
	const [acceptedPrivacy, setAcceptedPrivacy] = useState<boolean>(false);
	const [showTerms, setShowTerms] = useState<boolean>(false);
	const [showPrivacy, setShowPrivacy] = useState<boolean>(false);
	const [rememberMe, setRememberMe] = useState<boolean>(false);
	const [loading, setLoading] = useState<boolean>(false);
	const [demoLoading, setDemoLoading] = useState<boolean>(false);
	const [buttonDisabled, setButtonDisabled] = useState<boolean>(false);
	const [fieldErrors, setFieldErrors] = useState<Errors>({});
	const [captchaToken, setCaptchaToken] = useState<string>("");
	const hasFieldErrors: boolean = Object.values(fieldErrors).some((e) => !!e);
	const { logout, login, isAuthenticated } = useAuth();
	const { showToastSuccess, showToastError, showApiError } = useGlobalToast();
	const { showLoading, hideLoading } = useLoading();
	const contentRef = useRef<HTMLDivElement>(null);
	const [contentHeight, setContentHeight] = useState<number | "auto">("auto");
	const [contentVisible, setContentVisible] = useState(true);
	const [displayedMode, setDisplayedMode] = useState<AuthMode>(mode);
	const [displayedStep, setDisplayedStep] = useState<number>(registrationStep);
	const prevModeRef = useRef<string | null>(null);
	const { isTablet } = useViewport();

	useEffect(() => {
		const el = contentRef.current;
		if (!el) return;

		// Initial measure (covers first paint)
		setContentHeight(el.scrollHeight);

		const ro = new ResizeObserver(() => {
			// Use scrollHeight so overflow-hidden wrapper always fits full content
			setContentHeight(el.scrollHeight);
		});

		ro.observe(el);

		return () => ro.disconnect();
	}, []);

	useEffect(() => {
		const isInitialMount: boolean = prevModeRef.current === null;
		const modeKey = `${mode}-${registrationStep}`;

		if (prevModeRef.current === modeKey) return;

		if (isInitialMount) {
			prevModeRef.current = modeKey;
			return;
		}

		setContentVisible(false);
		const fadeOutTimer = setTimeout(() => {
			setDisplayedMode(mode);
			setDisplayedStep(registrationStep);
			prevModeRef.current = modeKey;

			requestAnimationFrame(() => {
				setTimeout(() => {
					setContentVisible(true);
				}, 300);
			});
		}, 150);

		return () => clearTimeout(fadeOutTimer);
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

	const handleInputChange = (e: SyntheticEvent): void => {
		const { name, value } = e.target;
		setFormData(
			(prev: FormData): FormData => ({
				...prev,
				[name]: value,
			})
		);

		setFieldErrors((prev: Errors): Errors => {
			const next = { ...prev };
			if (next[name as keyof Errors]) delete next[name as keyof Errors];
			if (name === "password" && next.confirmPassword) delete next.confirmPassword;
			return next;
		});
	};

	const handleFieldError = (key: string, message: string | null): void => {
		setFieldErrors((prev: Errors): Errors => ({ ...prev, [key]: message ?? "" }));
	};

	const resetForm = (): void => {
		setFormData(defaultFormData);
		setAcceptedTerms(false);
		setAcceptedPrivacy(false);
		setFieldErrors({});
		setResetToken("");
		setRegistrationStep(1);
		setCaptchaToken("");
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
			const step: number = currentStep ?? registrationStep;
			if (step === 1) {
				if (!formData.email || !/\S+@\S+\.\S+/.test(formData.email)) {
					errors.email = "Please provide a valid email address.";
				}
				if (!formData.password) {
					errors.password = "Password is required.";
				} else if (formData.password.length < (config?.min_password_length ?? 0)) {
					errors.password = `Password must be at least ${config?.min_password_length} characters long.`;
				}

				if (!formData.confirmPassword) {
					errors.confirmPassword = "Please confirm your password.";
				} else if (formData.password !== formData.confirmPassword) {
					errors.confirmPassword = "Passwords do not match.";
				}
			} else if (step === 2) {
				if (!formData.firstName || formData.firstName.trim().length === 0) {
					errors.firstName = "First name is required.";
				}

				if (!formData.lastName || formData.lastName.trim().length === 0) {
					errors.lastName = "Last name is required.";
				}
			} else if (step === 3) {
				if (!acceptedTerms) {
					errors.terms = "You must accept the Terms and Conditions to register.";
				}

				if (!acceptedPrivacy) {
					errors.privacy = "You must accept the Privacy Policy to register.";
				}

				if (!captchaToken) {
					errors.captcha = "Please complete the CAPTCHA to continue.";
				}
			}

			return errors;
		}

		if (["login", "forgotPassword"].includes(mode)) {
			if (!formData.email || !/\S+@\S+\.\S+/.test(formData.email)) {
				errors.email = "Please provide a valid email address.";
			}
		}

		if (["login", "resetPassword"].includes(mode)) {
			if (!formData.password) {
				errors.password = "Password is required.";
			} else if (mode === "resetPassword" && formData.password.length < (config?.min_password_length ?? 0)) {
				errors.password = `Password must be at least ${config?.min_password_length} characters long.`;
			}
		}

		if (mode === "resetPassword") {
			if (!formData.confirmPassword) {
				errors.confirmPassword = "Please confirm your password.";
			} else if (formData.password !== formData.confirmPassword) {
				errors.confirmPassword = "Passwords do not match.";
			}
		}

		return errors;
	};

	const handleLogin = async (): Promise<void> => {
		const errors: Errors = validateForm();
		setFieldErrors(errors);
		const errorTitle: string = "Login Failed";

		if (Object.keys(errors).length > 0) return;

		setLoading(true);
		setButtonDisabled(true);

		try {
			const result: GenericResponse = await login(formData.email, formData.password, rememberMe);

			if (result.success) {
				navigate("/dashboard");
			} else {
				showToastError(result.message, errorTitle);
			}
		} catch (error) {
			showApiError(error, errorTitle, "An unknown error occurred during login.");
		} finally {
			setLoading(false);
			setButtonDisabled(false);
		}
	};

	const handleNextStep = (): void => {
		const errors: Errors = validateForm(registrationStep);
		setFieldErrors(errors);

		if (Object.keys(errors).length > 0) return;

		setRegistrationStep(registrationStep + 1);
	};

	const handlePreviousStep = (): void => {
		setRegistrationStep((prev: number): number => Math.max(1, prev - 1));
		setFieldErrors({});
	};

	const handleRegister = async (): Promise<void> => {
		const errors: Errors = validateForm(registrationStep);
		setFieldErrors(errors);
		const errorTitle: string = "Registration Failed";

		if (Object.keys(errors).length > 0) return;

		setLoading(true);
		setButtonDisabled(true);

		try {
			const result: ApiResponse<GenericResponse> = await authApi.register({
				email: formData.email,
				password: formData.password,
				first_name: formData.firstName,
				last_name: formData.lastName,
				captcha_token: captchaToken,
			});

			if (result.data.success) {
				switchToLogin();
				showToastSuccess(
					"Account created! Please check your email inbox to verify your account before logging in.",
					"Registration Successful"
				);
			} else {
				showToastError(result.data.message, errorTitle);
				setCaptchaToken("");
				setRegistrationStep(3);
			}
		} catch (error) {
			showApiError(error, errorTitle, "An unknown error occurred during registration.");
			// Turnstile tokens are single-use — clear so the user re-solves on the next attempt
			setCaptchaToken("");
			setRegistrationStep(1);
		} finally {
			setLoading(false);
			setButtonDisabled(false);
		}
	};

	const handleForgotPassword = async (): Promise<void> => {
		const errors: Errors = validateForm();
		setFieldErrors(errors);
		const errorTitle: string = "Error Sending Password Reset Link";

		if (Object.keys(errors).length > 0) return;

		setLoading(true);
		setButtonDisabled(true);

		try {
			const response: ApiResponse = await authApi.requestPasswordReset(formData.email);
			showToastSuccess(response.data.message, "Reset Link Sent");
		} catch (error) {
			showApiError(error, errorTitle, "An unknown error occurred while sending the password reset link.");
		} finally {
			setLoading(false);
			setButtonDisabled(false);
		}
	};

	const handleResetPassword = async (): Promise<void> => {
		const errors: Errors = validateForm();
		setFieldErrors(errors);
		const errorTitle: string = "Error Resetting Password";

		if (Object.keys(errors).length > 0) return;

		setLoading(true);
		setButtonDisabled(true);
		try {
			const response: ApiResponse = await authApi.resetPassword(resetToken, formData.password);
			showToastSuccess(response.data.message, "Password Reset Successful");
			switchToLogin();
		} catch (error) {
			showApiError(error, errorTitle, "An unknown error occurred while resetting your password.");
		} finally {
			setLoading(false);
			setButtonDisabled(false);
		}
	};

	const handleDemoLogin = async (): Promise<void> => {
		setDemoLoading(true);
		setButtonDisabled(true);
		const errorTitle: string = "Demo Login Failed";

		try {
			const result: GenericResponse = await login(config?.app_demo_username ?? "", "demo");
			if (result.success) {
				navigate("/dashboard");
			} else {
				showToastError(result.message, errorTitle);
			}
		} catch (error) {
			showApiError(error, errorTitle, "An unknown error occurred while trying to login with the demo account.");
		} finally {
			setDemoLoading(false);
			setButtonDisabled(false);
		}
	};

	const handleSubmit = (e: React.FormEvent<HTMLFormElement>): void => {
		e.preventDefault();

		if (mode === "resetPassword") {
			handleResetPassword().then();
		} else if (mode === "forgotPassword") {
			handleForgotPassword().then();
		} else if (mode === "login") {
			handleLogin().then();
		} else if (mode === "register") {
			if (registrationStep < 3) {
				handleNextStep();
			} else {
				handleRegister().then();
			}
		}
	};

	const handleTermsCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
		setAcceptedTerms(e.target.checked);
		if (fieldErrors.terms) {
			setFieldErrors((prev: Errors): Errors => ({ ...prev, terms: "" }));
		}
	};

	const handlePrivacyCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
		setAcceptedPrivacy(e.target.checked);
		if (fieldErrors.privacy) {
			setFieldErrors((prev: Errors): Errors => ({ ...prev, privacy: "" }));
		}
	};

	const handleShowTerms = (e: React.MouseEvent<HTMLButtonElement>): void => {
		e.preventDefault();
		setShowTerms(true);
	};

	const handleShowPrivacy = (e: React.MouseEvent<HTMLButtonElement>): void => {
		e.preventDefault();
		setShowPrivacy(true);
	};

	const emailField: ModalFormField = {
		key: "email",
		type: "text",
		label: "Email Address",
		icon: "bi bi-envelope-fill",
		placeholder: "Enter your email",
		autoComplete: "email",
		maxChars: config?.column_limits.email,
		validation: EmailValidation,
	};

	const passwordField: ModalFormField = {
		key: "password",
		type: "password",
		label: displayedMode === "resetPassword" ? "New Password" : "Password",
		icon: "bi bi-key-fill",
		placeholder: displayedMode === "resetPassword" ? "Enter your new password" : "Enter your password",
		autoComplete: displayedMode === "login" ? "current-password" : "new-password",
		helpText: ["register", "resetPassword"].includes(displayedMode)
			? `Password must be at least ${config?.min_password_length} characters long`
			: null,
		maxChars: config?.column_limits.password,
	};

	const confirmPasswordField: ModalFormField = {
		key: "confirmPassword",
		type: "password",
		label: "Confirm Password",
		icon: "bi bi-key-fill",
		placeholder: displayedMode === "resetPassword" ? "Confirm your new password" : "Confirm your password",
		autoComplete: "new-password",
		maxChars: config?.column_limits.password,
	};

	const firstNameField: ModalFormField = {
		key: "firstName",
		type: "text",
		label: "First Name",
		icon: "bi bi-person-fill",
		placeholder: "Enter your first name",
		maxChars: config?.column_limits.first_name,
	};

	const lastNameField: ModalFormField = {
		key: "lastName",
		type: "text",
		label: "Last Name",
		icon: "bi bi-person-fill",
		placeholder: "Enter your last name",
		maxChars: config?.column_limits.last_name,
	};

	const cardTitle: string =
		displayedMode === "resetPassword"
			? "Set New Password"
			: displayedMode === "forgotPassword"
				? "Reset Your Password"
				: displayedMode === "login"
					? "Login"
					: displayedStep === 1
						? "Get Started"
						: displayedStep === 2
							? "Tell Us About Yourself"
							: "Almost There";

	const termsField: ModalFormField = {
		key: "terms",
		type: "checkbox",
		label: (
			<span>
				I agree to the{" "}
				<button type="button" onClick={handleShowTerms} className="btn-link" style={{ cursor: "pointer" }}>
					Terms and Conditions
				</button>
			</span>
		),
	};

	const privacyField: ModalFormField = {
		key: "privacy",
		type: "checkbox",
		label: (
			<span>
				I agree to the{" "}
				<button type="button" onClick={handleShowPrivacy} className="btn-link" style={{ cursor: "pointer" }}>
					Privacy Policy
				</button>
			</span>
		),
	};

	const featureItems: Feature[] = [
		{
			icon: "bi bi-briefcase",
			text: "Manage your job applications",
			description: "Create and manage job application records with all the details you need",
		},
		{
			icon: "bi bi-person",
			text: "Keep track of your contacts",
			description: "Keep track of every person you interact with during your job search",
		},
		{
			icon: "bi bi-bar-chart",
			text: "Monitor application status, deadlines and upcoming interviews",
			description:
				"Keep track of application status, progress, upcoming interviews, and never miss important deadlines",
		},
		{
			icon: "bi bi-envelope-arrow-up",
			text: "Generate follow-up emails",
			description: "Automatically generate personalised follow-up email drafts for your applications",
		},
		{
			icon: "bi bi-stars",
			text: "Scrape & auto-rate job alert emails",
			description:
				"Automatically scrape job alerts from LinkedIn, Indeed and more, then rate them by your preferences to prioritise applications",
		},
	];

	if (isAuthenticated) {
		return (
			<div className="auth-page-wrapper">
				<div className="auth-form-panel">
					<div className="auth-container">
						<div className="d-flex flex-column align-items-center">
							<Spinner animation="border" variant="primary" />
							<p className="mt-3 text-muted">Redirecting to dashboard...</p>
						</div>
					</div>
				</div>
			</div>
		);
	}

	return (
		<div className="auth-page-wrapper">
			{/* Left branding panel - conditionally rendered based on screen size */}
			{!isTablet && (
				<div className="auth-branding-panel">
					<div className="branding-content">
						<div className="branding-logo">
							<JamLogo />
						</div>
						<h1 className="branding-title">Job Application Manager</h1>
						<p className="branding-tagline">
							Streamline your job search. Track applications, manage deadlines, and land your dream job.
						</p>
						<ul className="feature-list">
							{featureItems.map(
								(feature: Feature, index: number): JSX.Element => (
									<li key={index} className="feature-item">
										<div className="feature-icon">
											<i className={feature.icon}></i>
										</div>
										<span className="feature-text">{feature.text}</span>
										<div className="feature-tooltip">{feature.description}</div>
									</li>
								)
							)}
						</ul>
					</div>
				</div>
			)}

			{/* Right form panel */}
			<div className="auth-form-panel">
				<div className="auth-container">
					{isTablet && (
						<div className="auth-logo">
							<div className="logo-container logo-container-vertical">
								<div className="branding-logo" style={{ marginBottom: 0 }}>
									<JamLogo />
								</div>
								<div className="logo-text-below text-gradient-primary">Job Application Manager</div>
							</div>
						</div>
					)}

					<Card
						className="auth-card border-0"
						style={{
							height: contentHeight,
							overflow: "hidden",
						}}
					>
						<div
							ref={contentRef}
							style={{
								padding: "2.5rem",
								opacity: contentVisible ? 1 : 0,
								transition: "opacity 0.15s ease-in-out",
							}}
						>
							<Card.Body>
								<Card.Title className="text-primary">{cardTitle}</Card.Title>

								{displayedMode === "register" && (
									<div className="mb-3">
										<div className="d-flex justify-content-between align-items-center mb-2">
											<small className="text-muted">Step {displayedStep} of 3</small>
											{displayedStep > 1 && (
												<button
													type="button"
													onClick={handlePreviousStep}
													className="btn-link"
													disabled={buttonDisabled}
												>
													<i className="bi bi-arrow-left me-1"></i>Back
												</button>
											)}
										</div>
										<div className="progress" style={{ height: "3.6px" }}>
											<div
												className="progress-bar"
												role="progressbar"
												style={{ width: `${(displayedStep / 3) * 100}%` }}
												aria-valuenow={(displayedStep / 3) * 100}
												aria-valuemin={0}
												aria-valuemax={100}
											></div>
										</div>
									</div>
								)}

								{displayedMode === "forgotPassword" && (
									<p className="text-muted mb-4">
										Enter your email address and we'll send you a link to reset your password.
									</p>
								)}

								{displayedMode === "resetPassword" && (
									<p className="text-muted mb-4">
										Please enter your new password below. Make sure it's strong and secure.
									</p>
								)}

								<Form onSubmit={handleSubmit} autoComplete="on">
									{/* Registration Step 1 */}
									{displayedMode === "register" && displayedStep === 1 && (
										<>
											{renderFormField(
												emailField,
												formData,
												handleInputChange,
												fieldErrors,
												undefined,
												undefined,
												handleFieldError
											)}
											{renderFormField(
												passwordField,
												formData,
												handleInputChange,
												fieldErrors,
												undefined,
												undefined,
												handleFieldError
											)}
											{renderFormField(
												confirmPasswordField,
												formData,
												handleInputChange,
												fieldErrors,
												undefined,
												undefined,
												handleFieldError
											)}
										</>
									)}

									{/* Registration Step 2 */}
									{displayedMode === "register" && displayedStep === 2 && (
										<>
											{renderFormField(
												firstNameField,
												formData,
												handleInputChange,
												fieldErrors,
												undefined,
												undefined,
												handleFieldError
											)}
											{renderFormField(
												lastNameField,
												formData,
												handleInputChange,
												fieldErrors,
												undefined,
												undefined,
												handleFieldError
											)}
										</>
									)}

									{/* Registration Step 3 */}
									{displayedMode === "register" && displayedStep === 3 && (
										<>
											<span className="step3-label">
												<i className="bi bi-file-earmark-text"></i>
												Review our T&amp;C and Privacy Policy
											</span>
											{renderFormField(
												termsField,
												{ terms: acceptedTerms },
												// @ts-ignore
												handleTermsCheckboxChange,
												fieldErrors
											)}
											{renderFormField(
												privacyField,
												{ privacy: acceptedPrivacy },
												// @ts-ignore
												handlePrivacyCheckboxChange,
												fieldErrors
											)}

											<div className="captcha-section mb-3">
												<span className="step3-label">
													<i className="bi bi-shield-check"></i>
													Just checking that you are not a robot
												</span>
												<TurnstileWidget
													siteKey={config?.turnstile_site_key ?? ""}
													onVerify={(token: string) => {
														setCaptchaToken(token);
														setFieldErrors(
															(prev: Errors): Errors => ({ ...prev, captcha: "" })
														);
													}}
													onExpire={() => setCaptchaToken("")}
													onError={() => setCaptchaToken("")}
												/>
												{fieldErrors.captcha && (
													<div className="invalid-feedback d-block text-center mt-2">
														{fieldErrors.captcha}
													</div>
												)}
											</div>
										</>
									)}

									{/* Login Mode */}
									{displayedMode === "login" && (
										<>
											{renderFormField(
												emailField,
												formData,
												handleInputChange,
												fieldErrors,
												undefined,
												undefined,
												handleFieldError
											)}
											{renderFormField(
												passwordField,
												formData,
												handleInputChange,
												fieldErrors,
												undefined,
												undefined,
												handleFieldError
											)}
											<div className="d-flex justify-content-between align-items-center mb-3">
												<Form.Check
													type="checkbox"
													id="remember-me"
													label="Remember me"
													checked={rememberMe}
													onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
														setRememberMe(e.target.checked)
													}
													className="small"
												/>
												<button
													type="button"
													onClick={switchToForgotPassword}
													className="btn-link"
													disabled={buttonDisabled}
													id="forgot-password-link"
												>
													Forgot your password?
												</button>
											</div>
										</>
									)}

									{/* Forgot Password Mode */}
									{displayedMode === "forgotPassword" && (
										<>
											{renderFormField(
												emailField,
												formData,
												handleInputChange,
												fieldErrors,
												undefined,
												undefined,
												handleFieldError
											)}
										</>
									)}

									{/* Reset Password Mode */}
									{displayedMode === "resetPassword" && (
										<>
											{renderFormField(
												passwordField,
												formData,
												handleInputChange,
												fieldErrors,
												undefined,
												undefined,
												handleFieldError
											)}
											{renderFormField(
												confirmPasswordField,
												formData,
												handleInputChange,
												fieldErrors,
												undefined,
												undefined,
												handleFieldError
											)}
										</>
									)}

									{/* Action buttons */}
									<div className="d-grid gap-2 pt-1">
										<ActionButton
											type="submit"
											id="confirm-button"
											disabled={buttonDisabled || hasFieldErrors}
											loading={loading}
											className="fw-semibold"
											loadingText={
												displayedMode === "resetPassword"
													? "Resetting Password..."
													: displayedMode === "forgotPassword"
														? "Sending..."
														: displayedMode === "login"
															? "Signing in..."
															: displayedStep < 3
																? "Please wait..."
																: "Creating Account..."
											}
											defaultText={
												displayedMode === "resetPassword"
													? "Reset Password"
													: displayedMode === "forgotPassword"
														? "Send Reset Link"
														: displayedMode === "login"
															? "Sign In"
															: displayedStep < 3
																? "Continue"
																: "Create Account"
											}
											defaultIcon={
												displayedMode === "resetPassword"
													? "bi bi-shield-lock"
													: displayedMode === "forgotPassword"
														? "bi bi-envelope-paper"
														: displayedMode === "login"
															? "bi bi-box-arrow-in-right"
															: displayedStep < 3
																? "bi bi-arrow-right"
																: "bi bi-person-plus"
											}
										/>
									</div>
								</Form>

								<Card.Footer className="bg-transparent border-0 text-center">
									<small className="text-muted">
										{displayedMode === "resetPassword" || displayedMode === "forgotPassword" ? (
											<>
												Remember your password?{" "}
												<button
													type="button"
													onClick={switchToLogin}
													className="btn-link"
													disabled={buttonDisabled}
												>
													Back to Sign In
												</button>
											</>
										) : displayedMode === "login" ? (
											<>
												Don't have an account?{" "}
												<button
													type="button"
													id="switch-mode-button"
													onClick={switchToRegister}
													className="btn-link"
													disabled={buttonDisabled}
												>
													Sign Up
												</button>
											</>
										) : (
											<>
												Already have an account?{" "}
												<button
													type="button"
													id="switch-mode-button"
													onClick={switchToLogin}
													className="btn-link"
													disabled={buttonDisabled}
												>
													Sign In
												</button>
											</>
										)}
									</small>
								</Card.Footer>
							</Card.Body>
						</div>
					</Card>

					{/* Try the app button - only show on login mode */}
					<div className="try-app-container">
						<div className="try-app-divider">
							<span>or</span>
						</div>
						<ActionButton
							className="try-app-btn"
							onClick={handleDemoLogin}
							loading={demoLoading}
							disabled={buttonDisabled || hasFieldErrors || !config}
							defaultText="Try JAM with Demo Account"
							loadingText="Loading demo..."
							defaultIcon="bi bi-play-circle"
							variant="outline-primary"
							id={"try-app-btn"}
						/>
					</div>
				</div>
			</div>

			<TermsAndConditions show={showTerms} onHide={() => setShowTerms(false)} />
			<PrivacyPolicyModal show={showPrivacy} onHide={() => setShowPrivacy(false)} />
		</div>
	);
}

export default AuthForm;
