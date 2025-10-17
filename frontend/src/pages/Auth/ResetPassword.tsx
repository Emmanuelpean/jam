import React, { JSX, useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import "./Auth.css";
import { ReactComponent as JamLogo } from "../../assets/Logo.svg";
import { Alert, Card, Form } from "react-bootstrap";
import { Errors, FormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { authApi, ApiError } from "../../services/Api";

interface ResetPasswordFormData {
	password: string;
	confirmPassword: string;
}

interface PasswordStrength {
	hasMinLength: boolean;
	hasUpperCase: boolean;
	hasLowerCase: boolean;
	hasNumber: boolean;
}

function ResetPassword(): JSX.Element {
	const [searchParams] = useSearchParams();
	const [formData, setFormData] = useState<ResetPasswordFormData>({
		password: "",
		confirmPassword: "",
	});
	const [loading, setLoading] = useState<boolean>(false);
	const [fieldErrors, setFieldErrors] = useState<Errors>({});
	const [token, setToken] = useState<string>("");
	const [passwordStrength, setPasswordStrength] = useState<PasswordStrength>({
		hasMinLength: false,
		hasUpperCase: false,
		hasLowerCase: false,
		hasNumber: false,
	});
	const navigate = useNavigate();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const MIN_PASSWORD_LENGTH = parseInt(process.env.REACT_APP_MIN_PASSWORD_LENGTH || "8");

	document.documentElement.setAttribute("data-theme", "mixed-berry");

	useEffect(() => {
		const tokenParam = searchParams.get("token");
		if (!tokenParam) {
			showToastError(
				"Invalid or missing reset token. Please request a new password reset link.",
				"Invalid Token",
			);
			navigate("/forgot-password");
		} else {
			setToken(tokenParam);
		}
	}, [searchParams, navigate, showToastError]);

	useEffect(() => {
		setPasswordStrength({
			hasMinLength: formData.password.length >= MIN_PASSWORD_LENGTH,
			hasUpperCase: /[A-Z]/.test(formData.password),
			hasLowerCase: /[a-z]/.test(formData.password),
			hasNumber: /\d/.test(formData.password),
		});
	}, [formData.password, MIN_PASSWORD_LENGTH]);

	const handleInputChange = (e: SyntheticEvent): void => {
		const { name, value } = e.target;
		setFormData(
			(prev: ResetPasswordFormData): ResetPasswordFormData => ({
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

	const isPasswordValid = (): boolean => {
		return Object.values(passwordStrength).every(Boolean);
	};

	const validateForm = (): Errors => {
		const errors: Errors = {};

		if (!formData.password) {
			errors.password = "Password is required.";
		} else if (formData.password.length < MIN_PASSWORD_LENGTH) {
			errors.password = `Password must be at least ${MIN_PASSWORD_LENGTH} characters long.`;
		} else if (!isPasswordValid()) {
			errors.password = "Password does not meet all requirements.";
		}

		if (!formData.confirmPassword) {
			errors.confirmPassword = "Please confirm your password.";
		} else if (formData.password !== formData.confirmPassword) {
			errors.confirmPassword = "Passwords do not match.";
		}

		return errors;
	};

	const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
		e.preventDefault();

		const errors = validateForm();
		setFieldErrors(errors);

		if (Object.keys(errors).length > 0) {
			return;
		}

		setLoading(true);

		try {
			const response = await authApi.resetPassword(token, formData.password);
			showToastSuccess("Your password has been reset successfully. You can now log in.", "Password Reset");
			setTimeout(() => {
				navigate("/login");
			}, 2000);
		} catch (error) {
			const apiError = error as ApiError;
			if (apiError.status === 403) {
				showToastError(
					"This reset link has expired or is invalid. Please request a new one.",
					"Invalid or Expired Token",
				);
			} else {
				showToastError(apiError.message || "An error occurred. Please try again.", "Reset Failed");
			}
		} finally {
			setLoading(false);
		}
	};

	const passwordField: ModalFormField = {
		name: "password",
		type: "password",
		label: "New Password",
		icon: "bi bi-lock-fill",
		placeholder: "Enter new password",
		autoComplete: "new-password",
	};

	const confirmPasswordField: ModalFormField = {
		name: "confirmPassword",
		type: "password",
		label: "Confirm New Password",
		icon: "bi bi-lock-fill",
		placeholder: "Confirm new password",
		autoComplete: "new-password",
	};

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
					<Card.Title className="text-primary">Create New Password</Card.Title>
					<p className="text-muted mb-4">Please enter your new password below.</p>

					<Form onSubmit={handleSubmit} autoComplete="on">
						{FormField(passwordField, formData, handleInputChange, fieldErrors)}

						{formData.password && (
							<div className="password-requirements mb-3 p-3 bg-light rounded">
								<p className="small fw-semibold mb-2 text-muted">Password must contain:</p>
								<ul className="list-unstyled mb-0 small">
									<li className={passwordStrength.hasMinLength ? "text-success" : "text-muted"}>
										<i
											className={`bi ${passwordStrength.hasMinLength ? "bi-check-circle-fill" : "bi-circle"} me-2`}
										></i>
										At least {MIN_PASSWORD_LENGTH} characters
									</li>
									<li className={passwordStrength.hasUpperCase ? "text-success" : "text-muted"}>
										<i
											className={`bi ${passwordStrength.hasUpperCase ? "bi-check-circle-fill" : "bi-circle"} me-2`}
										></i>
										One uppercase letter
									</li>
									<li className={passwordStrength.hasLowerCase ? "text-success" : "text-muted"}>
										<i
											className={`bi ${passwordStrength.hasLowerCase ? "bi-check-circle-fill" : "bi-circle"} me-2`}
										></i>
										One lowercase letter
									</li>
									<li className={passwordStrength.hasNumber ? "text-success" : "text-muted"}>
										<i
											className={`bi ${passwordStrength.hasNumber ? "bi-check-circle-fill" : "bi-circle"} me-2`}
										></i>
										One number
									</li>
								</ul>
							</div>
						)}

						{FormField(confirmPasswordField, formData, handleInputChange, fieldErrors)}

						<div className="d-grid">
							<ActionButton
								id="reset-password-button"
								type="submit"
								disabled={loading || !token}
								loading={loading}
								className="fw-semibold"
								loadingText="Resetting Password..."
								defaultText="Reset Password"
								defaultIcon="bi bi-key-fill"
							/>
						</div>
					</Form>

					<Card.Footer className="bg-transparent border-top-0 text-center">
						<small className="text-muted">
							Remember your password?{" "}
							<button
								type="button"
								onClick={() => navigate("/login")}
								className="btn-link text-decoration-none fw-semibold text-primary p-0 border-0 bg-transparent"
								style={{ cursor: "pointer" }}
							>
								Back to Login
							</button>
						</small>
					</Card.Footer>
				</Card.Body>
			</Card>
		</div>
	);
}

export default ResetPassword;
