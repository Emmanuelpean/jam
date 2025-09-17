import React, { useEffect, useState } from "react";
import { Card, Col, Form, Row } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { api, ApiError } from "../../services/Api";
import { THEMES } from "../../utils/Theme";
import { renderFormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import "./UserSettingsPage.css";
import { getTableIcon } from "../../components/rendering/view/ViewRenders";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { findByKey } from "../../utils/Utils";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { FormField } from "../../components/rendering/form/FormRenders";
import { ValidationErrors } from "../../components/modals/GenericModal/GenericModal";
import { useLoading } from "../../contexts/LoadingContext";

interface FormData {
	email: string;
	current_password?: string;
	new_password?: string;
	confirm_password?: string;
	chase_threshold?: number;
	deadline_threshold?: number;
	update_limit?: number;
}

const UserSettingsPage: React.FC = () => {
	const { currentUser, token } = useAuth();
	const [formData, setFormData] = useState<FormData>({
		chase_threshold: 0,
		confirm_password: "",
		current_password: "",
		deadline_threshold: 0,
		email: "",
		new_password: "",
		update_limit: 0,
	});
	const { showSuccess, showError } = useGlobalToast();
	const [errors, setErrors] = useState<ValidationErrors>({});
	const [submitting, setSubmitting] = useState<boolean>(false);
	const { showLoading, hideLoading } = useLoading();

	const MIN_PASSWORD_LENGTH: number = parseInt(process.env.REACT_APP_MIN_PASSWORD_LENGTH || "8");

	// Load user settings on component mount
	useEffect(() => {
		const loadUserSettings = async () => {
			if (!token) return;

			showLoading("Loading User Settings...");
			try {
				const response = await api.get("users/me", token);

				setFormData(() => ({
					email: response.email || "",
					chase_threshold: response.chase_threshold,
					deadline_threshold: response.deadline_threshold,
					update_limit: response.update_limit,
				}));
			} catch (error) {
				console.error("Failed to load user settings:", error);
				showError("Failed to load user settings. Please refresh the page.");
			} finally {
				hideLoading();
			}
		};

		loadUserSettings().then(() => {});
	}, [token]);

	const handleInputChange = (e: SyntheticEvent): void => {
		const { name, value } = e.target;
		setFormData((prev) => ({
			...prev,
			[name]: value,
		}));

		// Clear specific field errors when user starts typing
		if (errors[name]) {
			setErrors((prev) => ({
				...prev,
				[name]: "",
			}));
		}
	};

	const validateForm = (): boolean => {
		const newErrors: ValidationErrors = {};

		// Check if any changes were made
		const hasAccountChanges =
			formData.email !== currentUser?.email || formData.new_password || formData.confirm_password;

		// If making account changes, current password is required
		if (hasAccountChanges && !formData.current_password) {
			newErrors.current_password = "Current password is required to update email or password";
		}

		// Email validation
		if (formData.email && !/\S+@\S+\.\S+/.test(formData.email)) {
			newErrors.email = "Email format is invalid";
		}

		// New password validation (only if changing password)
		if (formData.new_password || formData.confirm_password) {
			if (formData.new_password && formData.new_password.length < MIN_PASSWORD_LENGTH) {
				newErrors.new_password = `New password must be at least ${MIN_PASSWORD_LENGTH} characters long`;
			}
			if (formData.new_password !== formData.confirm_password) {
				newErrors.confirm_password = "Passwords do not match";
			}
		}

		// Dashboard settings validation
		if (
			formData.chase_threshold !== undefined &&
			(formData.chase_threshold < 1 || formData.chase_threshold > 365)
		) {
			newErrors.chase_threshold = "Chase threshold must be between 1 and 365 days";
		}
		if (
			formData.deadline_threshold !== undefined &&
			(formData.deadline_threshold < 1 || formData.deadline_threshold > 365)
		) {
			newErrors.deadline_threshold = "Deadline threshold must be between 1 and 365 days";
		}
		if (formData.update_limit !== undefined && (formData.update_limit < 1 || formData.update_limit > 1000)) {
			newErrors.update_limit = "Update limit must be between 1 and 1000";
		}

		setErrors(newErrors);
		return Object.keys(newErrors).length === 0;
	};

	const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
		e.preventDefault();

		if (!validateForm()) {
			return;
		}

		setSubmitting(true);

		try {
			const updateData: {
				current_password?: string;
				email?: string;
				password?: string;
				chase_threshold?: number;
				deadline_threshold?: number;
				update_limit?: number;
			} = {};

			// Add account changes if current password is provided
			if (formData.current_password) {
				updateData.current_password = formData.current_password;

				if (formData.email && formData.email !== currentUser?.email) {
					updateData.email = formData.email;
				}

				if (formData.new_password) {
					updateData.password = formData.new_password;
				}
			}

			// Add dashboard settings
			if (formData.chase_threshold !== undefined) {
				updateData.chase_threshold = formData.chase_threshold;
			}
			if (formData.deadline_threshold !== undefined) {
				updateData.deadline_threshold = formData.deadline_threshold;
			}
			if (formData.update_limit !== undefined) {
				updateData.update_limit = formData.update_limit;
			}

			await api.put("users/me", updateData, token);

			// Success case - clear password fields but keep other data
			if (formData.new_password) {
				setFormData((prev) => ({
					...prev,
					new_password: "",
					confirm_password: "",
				}));
			}
			showSuccess("User settings updated successfully.");
		} catch (error: unknown) {
			const apiError = error as ApiError;
			if (apiError.status === 400) {
				showError("Email is already in use. Please try a different email.");
			} else if (apiError.status === 401) {
				showError("Current password is incorrect. Please try again.");
			} else {
				showError("An unknown error occurred. Please try again later.");
			}
		}
		setSubmitting(false);
	};

	const emailField: FormField = {
		name: "email",
		label: "Email Address",
		type: "text",
		placeholder: "Enter your email address",
	};

	const currentPasswordField: FormField = {
		name: "current_password",
		type: "password",
		label: "Current Password",
		placeholder: "Enter your current password",
		helpText: "Required to change your email or password",
	};

	const newPasswordField: FormField = {
		name: "new_password",
		type: "password",
		label: "New Password",
		placeholder: "Enter new password",
	};

	const confirmPasswordField: FormField = {
		name: "confirm_password",
		type: "password",
		label: "Confirm New Password",
		placeholder: "Confirm new password",
	};

	const chaseThresholdField: FormField = {
		name: "chase_threshold",
		type: "number",
		label: "Chase Threshold (days)",
		placeholder: "10",
		helpText: "Jobs below this threshold will be flagged for follow-up",
	};

	const deadlineThresholdField: FormField = {
		name: "deadline_threshold",
		type: "number",
		label: "Deadline Threshold (days)",
		placeholder: "3",
		helpText: "Jobs within this threshold are considered near deadline",
	};

	const updateLimitField: FormField = {
		name: "update_limit",
		type: "number",
		label: "Update Display Limit",
		placeholder: "50",
		helpText: "Maximum number of job updates to show",
	};

	return (
		<div className="settings-wrapper">
			<Card className="settings-card border-0 shadow-sm">
				<Card.Header className="settings-header border-0 p-0">
					<div className="d-flex align-items-center p-4">
						<div className="header-icon-wrapper me-3">
							<i className={`bi ${getTableIcon("Users")}`}></i>
						</div>
						<div>
							<h4 className="mb-0 fw-bold text-dark">User Settings</h4>
							<small className="text-muted">Manage your account preferences</small>
						</div>
					</div>
				</Card.Header>

				<Card.Body className="p-0">
					<Form onSubmit={handleSubmit} className="p-4">
						{errors.general && <div className="alert alert-danger mb-4">{errors.general}</div>}

						<Col md={12} className="mb-3">
							{renderFormField(currentPasswordField, formData, handleInputChange, errors)}
						</Col>

						{/* Account Settings Section */}
						<div className="settings-section">
							<div className="section-header mb-4">
								<h5 className="section-title">
									<i className="bi bi-envelope me-2 text-primary"></i>
									Account Settings
								</h5>
							</div>
							{renderFormField(emailField, formData, handleInputChange, errors)}
						</div>

						{/* Security Section */}
						<div className="settings-section">
							<div className="section-header mb-4">
								<h5 className="section-title">
									<i className="bi bi-shield-lock me-2 text-primary"></i>
									Security
								</h5>
							</div>

							<div className="password-hint mb-4"></div>

							<Row>
								<Col md={6} className="mb-3">
									{renderFormField(newPasswordField, formData, handleInputChange, errors)}
								</Col>
								<Col md={6} className="mb-3">
									{renderFormField(confirmPasswordField, formData, handleInputChange, errors)}
								</Col>
							</Row>
						</div>

						{/* Dashboard Section */}
						<div className="settings-section">
							<div className="section-header mb-4">
								<h5 className="section-title">
									<i className="bi bi-speedometer2 me-2 text-primary"></i>
									Dashboard Settings
								</h5>
							</div>
							<Row>
								<Col md={4} className="mb-3">
									{renderFormField(chaseThresholdField, formData, handleInputChange, errors)}
								</Col>
								<Col md={4} className="mb-3">
									{renderFormField(deadlineThresholdField, formData, handleInputChange, errors)}
								</Col>
								<Col md={4} className="mb-3">
									{renderFormField(updateLimitField, formData, handleInputChange, errors)}
								</Col>
							</Row>
						</div>

						{/* Appearance Section */}
						<div className="settings-section">
							<div className="section-header mb-4">
								<h5 className="section-title">
									<i className="bi bi-palette me-2 text-primary"></i>
									Appearance
								</h5>
							</div>

							<div className="form-group-enhanced">
								<p className="form-label-enhanced" id="theme-hint">
									{findByKey(THEMES, currentUser?.theme)?.name} is not your favourite flavour of JAM?!
									You can easily pick another flavour by clicking on the JAM logo in the sidebar.
								</p>
							</div>
						</div>

						<div className="settings-actions">
							<ActionButton
								id="confirm-button"
								type="submit"
								disabled={submitting}
								loading={submitting}
								className="save-button"
								loadingText="Saving Changes..."
								defaultText="Save Changes"
								defaultIcon="bi bi-check-circle"
							/>
						</div>
					</Form>
				</Card.Body>
			</Card>
		</div>
	);
};

export default UserSettingsPage;
