import React, { JSX, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import "./Auth.css";
import { ReactComponent as JamLogo } from "../../assets/Logo.svg";
import { Card, Form, Spinner } from "react-bootstrap";
import TermsAndConditions from "./TermsConditions";
import { Errors, renderModalFormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { FormData, AuthResponse } from "../../contexts/AuthContext";

function AuthForm(): JSX.Element {
	const [isLogin, setIsLogin] = useState<boolean>(true);
	const [formData, setFormData] = useState<FormData>({
		email: "",
		password: "",
		confirmPassword: "",
	});
	const [acceptedTerms, setAcceptedTerms] = useState<boolean>(false);
	const [showTerms, setShowTerms] = useState<boolean>(false);
	const [loading, setLoading] = useState<boolean>(false);
	const [fieldErrors, setFieldErrors] = useState<Errors>({});
	const { login, register, isAuthenticated } = useAuth();
	const navigate = useNavigate();
	const location = useLocation();
	const { showSuccess, showError } = useGlobalToast();
	const MIN_PASSWORD_LENGTH = parseInt(process.env.REACT_APP_MIN_PASSWORD_LENGTH || "8");

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

	const handleInputChange = (e: SyntheticEvent): void => {
		const { name, value } = e.target;
		setFormData(
			(prev: FormData): FormData => ({
				...prev,
				[name]: value,
			}),
		);

		// Clear field errors when user starts typing
		if (fieldErrors[name as keyof Errors]) {
			setFieldErrors((prev: Errors) => ({
				...prev,
				[name]: "",
			}));
		}
	};

	const switchMode = (): void => {
		setIsLogin(!isLogin);
		setFieldErrors({});
		if (!isLogin) {
			setFormData((prev) => ({
				...prev,
				confirmPassword: "",
			}));
			setAcceptedTerms(false);
		}
		// Update URL without navigation
		window.history.replaceState(null, "", isLogin ? "register" : "login");
	};

	const resetForm = (): void => {
		setFormData({
			email: "",
			password: "",
			confirmPassword: "",
		});
		setAcceptedTerms(false);
		setFieldErrors({});
	};

	const validateForm = (): Errors => {
		const errors: Errors = {};

		// Email validation
		if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
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

	const handleAuthResponse = (result: AuthResponse, isLoginAction: boolean): void => {
		if (result.success) {
			if (isLoginAction) {
				navigate("/dashboard");
			} else {
				// Registration successful
				setIsLogin(true);
				resetForm();
				navigate("/login");
				showSuccess("Account created successfully! You can now log in.", "Registration Successful");
			}
		} else {
			// Use centralized error messages from AuthContext
			const title = isLoginAction ? "Login Failed" : "Registration Failed";
			const message = result.error || "An unknown error occurred";
			showError(message, title);
		}
	};

	const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
		e.preventDefault();

		// Validate form
		const errors = validateForm();
		setFieldErrors(errors);

		if (Object.keys(errors).length > 0) {
			return;
		}

		setLoading(true);

		try {
			const result: AuthResponse = isLogin
				? await login(formData.email, formData.password)
				: await register(formData.email, formData.password);

			handleAuthResponse(result, isLogin);
		} catch (error) {
			// Fallback error handling for unexpected errors
			const title = isLogin ? "Login Error" : "Registration Error";
			const message = isLogin
				? "Failed to login. An unknown error occurred"
				: "Failed to create an account. An unknown error occurred";
			showError(message, title);
		} finally {
			setLoading(false);
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
		label: "Password",
		icon: "bi bi-lock-fill",
		placeholder: "Enter your password",
		autoComplete: isLogin ? "current-password" : "new-password",
		helpText: !isLogin ? `Password must be at least ${MIN_PASSWORD_LENGTH} characters long` : null,
	};

	const confirmPasswordField: ModalFormField = {
		name: "confirmPassword",
		type: "password",
		label: "Confirm Password",
		icon: "bi bi-lock-fill",
		placeholder: "Confirm your password",
		autoComplete: "new-password",
		tabIndex: isLogin ? -1 : 0,
	};

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
					<JamLogo style={{ height: "175px", width: "auto" }} />
					<div className="logo-text-below text-gradient-primary" style={{ fontSize: "50px" }}>
						Job Application Manager
					</div>
				</div>
			</div>

			<Card className="auth-card border-0 auth-card-animated">
				<Card.Body>
					<Card.Title className="text-primary">{isLogin ? "Login" : "Create Account"}</Card.Title>

					<Form onSubmit={handleSubmit} autoComplete="on">
						{renderModalFormField(emailField, formData, handleInputChange, fieldErrors)}

						{renderModalFormField(passwordField, formData, handleInputChange, fieldErrors)}

						<div
							className={`auth-field-container ${!isLogin ? "auth-field-visible" : "auth-field-hidden"}`}
						>
							{renderModalFormField(confirmPasswordField, formData, handleInputChange, fieldErrors)}
						</div>
						<div
							className={`auth-field-container ${!isLogin ? "auth-field-visible" : "auth-field-hidden"}`}
						>
							{renderModalFormField(
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
