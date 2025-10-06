import React, { useState } from "react";
import { Button, Card, Col, Form, Row } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { api, ApiError, exportApi } from "../../services/Api";
import { THEMES } from "../../utils/Theme";
import { renderModalFormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import "./UserSettingsPage.css";
import { getTableIcon } from "../../components/rendering/view/Icons";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { findByKey } from "../../utils/Utils";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { ValidationErrors } from "../../components/modals/DataModal/DataModal";

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
	const { currentUser, token, updateCurrentUser } = useAuth();
	const [formData, setFormData] = useState<FormData>(() => ({
		email: currentUser?.email || "",
		chase_threshold: currentUser?.chase_threshold || 0,
		deadline_threshold: currentUser?.deadline_threshold || 0,
		update_limit: currentUser?.update_limit || 0,
		current_password: "",
		new_password: "",
		confirm_password: "",
	}));
	const { showToastSuccess, showToastError } = useGlobalToast();
	const [errors, setErrors] = useState<ValidationErrors>({});
	const [submitting, setSubmitting] = useState<boolean>(false);

	const MIN_PASSWORD_LENGTH: number = parseInt(process.env.REACT_APP_MIN_PASSWORD_LENGTH || "8");

	const downloadJobsExport = async (token: string | null) => {
		if (!token) return;
		try {
			await exportApi.download("jobs_export.zip", token);
			showToastSuccess("Data downloaded");
		} catch (e) {
			showToastError("Failed to download data");
		}
	};

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

			const response = await api.put("users/me", updateData, token);

			// Update the context with the API response
			updateCurrentUser(response);

			// Success case - clear password fields but keep other data
			if (formData.new_password) {
				setFormData((prev) => ({
					...prev,
					new_password: "",
					confirm_password: "",
				}));
			}
			showToastSuccess("User settings updated successfully.");
		} catch (error: unknown) {
			const apiError = error as ApiError;
			if (apiError.status === 400) {
				showToastError("Email is already in use. Please try a different email.");
			} else if (apiError.status === 401) {
				showToastError("Current password is incorrect. Please try again.");
			} else {
				showToastError("An unknown error occurred. Please try again later.");
			}
		}
		setSubmitting(false);
	};

	const emailField: ModalFormField = {
		name: "email",
		label: "Email Address",
		type: "text",
		placeholder: "Enter your email address",
	};

	const currentPasswordField: ModalFormField = {
		name: "current_password",
		type: "password",
		label: "Current Password",
		placeholder: "Enter your current password",
		helpText: "Required to change your email or password",
	};

	const newPasswordField: ModalFormField = {
		name: "new_password",
		type: "password",
		label: "New Password",
		placeholder: "Enter new password",
	};

	const confirmPasswordField: ModalFormField = {
		name: "confirm_password",
		type: "password",
		label: "Confirm New Password",
		placeholder: "Confirm new password",
	};

	const chaseThresholdField: ModalFormField = {
		name: "chase_threshold",
		type: "number",
		label: "Chase Threshold (days)",
		placeholder: "10",
		helpText: "Jobs below this threshold will be flagged for follow-up",
	};

	const deadlineThresholdField: ModalFormField = {
		name: "deadline_threshold",
		type: "number",
		label: "Deadline Threshold (days)",
		placeholder: "3",
		helpText: "Jobs within this threshold are considered near deadline",
	};

	const updateLimitField: ModalFormField = {
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
							{renderModalFormField(currentPasswordField, formData, handleInputChange, errors)}
						</Col>

						{/* Account Settings Section */}
						<div className="settings-section">
							<div className="section-header mb-4">
								<h5 className="section-title">
									<i className="bi bi-envelope me-2 text-primary"></i>
									Account Settings
								</h5>
							</div>
							{renderModalFormField(emailField, formData, handleInputChange, errors)}
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
									{renderModalFormField(newPasswordField, formData, handleInputChange, errors)}
								</Col>
								<Col md={6} className="mb-3">
									{renderModalFormField(confirmPasswordField, formData, handleInputChange, errors)}
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
									{renderModalFormField(chaseThresholdField, formData, handleInputChange, errors)}
								</Col>
								<Col md={4} className="mb-3">
									{renderModalFormField(deadlineThresholdField, formData, handleInputChange, errors)}
								</Col>
								<Col md={4} className="mb-3">
									{renderModalFormField(updateLimitField, formData, handleInputChange, errors)}
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

						{/* Download Section */}
						<div className="settings-section">
							<div className="section-header mb-4">
								<h5 className="section-title">
									<i className="bi bi-palette me-2 text-primary"></i>
									Download Data
								</h5>
							</div>

							<Button className="w-100" onClick={() => downloadJobsExport(token)}>
								<i className="bi bi-download me-2"></i>
								Download Data
							</Button>
						</div>

						<div className="settings-actions">
							<div className="horizontal-bar mb-3"></div>
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
