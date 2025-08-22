import React, { useState } from "react";
import { Card, Col, Form, Row } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { api } from "../../services/Api";
import { getThemeByKey } from "../../utils/Theme";
import { ActionButton, renderInputField } from "../../components/rendering/form/WidgetRenders";
import "./UserSettingsPage.css";
import { getTableIcon } from "../../components/rendering/view/Renders";
import { useGlobalToast } from "../../hooks/useNotificationToast";

const UserSettingsPage = () => {
	const { currentUser, token } = useAuth();
	const [formData, setFormData] = useState({
		email: "",
		currentPassword: "",
		newPassword: "",
		confirmPassword: "",
	});
	const { showSuccess, showError } = useGlobalToast();
	const [errors, setErrors] = useState({});
	const [loading, setLoading] = useState(false);

	// Get minimum password length from environment variables
	const MIN_PASSWORD_LENGTH = parseInt(process.env.REACT_APP_MIN_PASSWORD_LENGTH);

	const handleInputChange = (e) => {
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

	const validateForm = () => {
		const newErrors = {};

		// Current password validation
		if (!formData.currentPassword) {
			newErrors.currentPassword = "Current password is required to update email or password";
		}

		// Email validation
		if (formData.email && !/\S+@\S+\.\S+/.test(formData.email)) {
			newErrors.email = "Email format is invalid";
		}

		// New password validation (only if changing password)
		if (formData.newPassword || formData.confirmPassword) {
			if (formData.newPassword.length < MIN_PASSWORD_LENGTH) {
				newErrors.newPassword = `New password must be at least ${MIN_PASSWORD_LENGTH} characters long`;
			}
			if (formData.newPassword !== formData.confirmPassword) {
				newErrors.confirmPassword = "Passwords do not match";
			}
		}

		if (!formData.email && !formData.newPassword && !formData.confirmPassword) {
			newErrors.email = "Please enter ";
		}

		setErrors(newErrors);
		return Object.keys(newErrors).length === 0;
	};

	const handleSubmit = async (e) => {
		e.preventDefault();

		if (!validateForm()) {
			return;
		}

		setLoading(true);

		try {
			const updateData = {
				current_password: formData.currentPassword,
			};

			if (formData.email) {
				updateData.email = formData.email;
			}

			if (formData.newPassword) {
				updateData.password = formData.newPassword;
			}

			await api.put("users/me", updateData, token);

			// Success case - the request completed successfully
			if (formData.newPassword) {
				setFormData({
					currentPassword: "",
					newPassword: "",
					confirmPassword: "",
					email: formData.email,
				});
			}
			showSuccess("User data updated successfully.");
		} catch (error) {
			if (error.status === 400) {
				showError("Email is already in use. Please try a different email.");
			} else if (error.status === 401) {
				showError("Current password is incorrect. Please try again.");
			} else {
				showError("An unknown error occurred. Please try again later.");
			}
		}
		setLoading(false);
	};

	const emailField = {
		name: "email",
		type: "text",
		placeholder: "Enter your email address",
		autoComplete: "off",
	};

	const currentPasswordField = {
		name: "currentPassword",
		type: "password",
		placeholder: "Enter your current password",
		helpText: "Required to change your email or password",
	};

	const newPasswordField = {
		name: "newPassword",
		type: "password",
		placeholder: "Enter new password",
	};

	const confirmPasswordField = {
		name: "confirmPassword",
		type: "password",
		placeholder: "Confirm new password",
	};

	return (
		<div className="settings-wrapper">
			<Row className="justify-content-center">
				<Col xl={6} lg={8} md={10}>
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
								<Col md={12} className="mb-3">
									<Form.Group className="form-group-enhanced">
										<Form.Label className="form-label-enhanced">Current Password</Form.Label>
										{renderInputField(currentPasswordField, formData, handleInputChange, errors)}
									</Form.Group>
								</Col>

								{/* Account Settings Section */}
								<div className="settings-section">
									<div className="section-header mb-4">
										<h5 className="section-title">
											<i className="bi bi-envelope me-2 text-primary"></i>
											Account Settings
										</h5>
									</div>

									<Form.Group className="form-group-enhanced">
										<Form.Label className="form-label-enhanced">Email Address</Form.Label>
										{renderInputField(emailField, formData, handleInputChange, errors)}
									</Form.Group>
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
											<Form.Group className="form-group-enhanced">
												<Form.Label className="form-label-enhanced">New Password</Form.Label>
												{renderInputField(
													newPasswordField,
													formData,
													handleInputChange,
													errors,
												)}
											</Form.Group>
										</Col>
										<Col md={6} className="mb-3">
											<Form.Group className="form-group-enhanced">
												<Form.Label className="form-label-enhanced">
													Confirm New Password
												</Form.Label>
												{renderInputField(
													confirmPasswordField,
													formData,
													handleInputChange,
													errors,
												)}
											</Form.Group>
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
										<Form.Label className="form-label-enhanced">
											{getThemeByKey(formData.theme)?.name} is not your favourite flavour of JAM?!
											You can easily pick another flavour by clicking on the JAM logo in the
											sidebar.
										</Form.Label>
									</div>
								</div>

								<div className="settings-actions">
									<ActionButton
										id="confirm-button"
										type="submit"
										disabled={
											loading ||
											(!formData.email && !formData.newPassword && !formData.confirmPassword)
										}
										loading={loading}
										className="save-button"
										loadingText="Saving Changes..."
										defaultText="Save Account Changes"
										defaultIcon="bi bi-check-circle"
									/>
								</div>
							</Form>
						</Card.Body>
					</Card>
				</Col>
			</Row>
		</div>
	);
};

export default UserSettingsPage;
