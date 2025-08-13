import React, { useEffect, useState } from "react";
import { Button, Card, Col, Form, Row } from "react-bootstrap";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../services/Api";
import { isValidTheme, getThemeByKey } from "../utils/Theme";
import { renderInputField } from "../components/rendering/WidgetRenders";
import "./UserSettingsPage.css";
import { getTableIcon } from "../components/rendering/Renders";

const UserSettingsPage = () => {
	const { currentUser, token } = useAuth();
	const [formData, setFormData] = useState({
		email: "",
		currentPassword: "",
		newPassword: "",
		confirmPassword: "",
		theme: "",
	});
	const [errors, setErrors] = useState({});

	useEffect(() => {
		if (currentUser) {
			setFormData((prevData) => ({
				...prevData,
				email: currentUser.email || "",
				theme: currentUser.theme || "mixed-berry",
			}));
		}
	}, [currentUser]);

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

	// Handle immediate theme change
	const handleThemeChange = async (e) => {
		const { value: themeKey } = e.target;

		// Update form data
		setFormData((prev) => ({
			...prev,
			theme: themeKey,
		}));

		document.documentElement.setAttribute("data-theme", themeKey);
		localStorage.setItem("theme", themeKey);

		try {
			await api.put("users/me", { theme: themeKey }, token);
		} catch (error) {
			error.theme = "Could not save the theme. Please try again later.";
			setErrors((prev) => ({
				...prev,
				theme: error.theme,
			}));
		}
	};

	const validateForm = () => {
		const newErrors = {};

		// Check if user is trying to update anything that requires current password
		const isUpdatingEmail = formData.email !== currentUser?.email;
		const isUpdatingPassword = formData.newPassword || formData.confirmPassword;

		// Current password is required if updating email or password
		if (isUpdatingEmail || isUpdatingPassword) {
			if (!formData.currentPassword) {
				if (isUpdatingEmail && isUpdatingPassword) {
					newErrors.currentPassword = "Current password is required to update email and password";
				} else if (isUpdatingEmail) {
					newErrors.currentPassword = "Current password is required to update email address";
				} else {
					newErrors.currentPassword = "Current password is required to change password";
				}
			}
		}

		// Email validation
		if (!formData.email.trim()) {
			newErrors.email = "Email is required";
		} else if (!/\S+@\S+\.\S+/.test(formData.email)) {
			newErrors.email = "Email format is invalid";
		}

		// Password validation (only if changing password)
		if (isUpdatingPassword) {
			if (!formData.newPassword) {
				newErrors.newPassword = "New password is required";
			} else if (formData.newPassword.length < 6) {
				newErrors.newPassword = "New password must be at least 6 characters long";
			}
			if (formData.newPassword !== formData.confirmPassword) {
				newErrors.confirmPassword = "Passwords do not match";
			}
		}

		// Theme validation
		if (!isValidTheme(formData.theme)) {
			newErrors.theme = "Invalid theme selected";
		}

		setErrors(newErrors);
		return Object.keys(newErrors).length === 0;
	};

	const handleSubmit = async (e) => {
		e.preventDefault();

		if (!validateForm()) {
			return;
		}

		try {
			const updateData = {
				email: formData.email,
				current_password: formData.currentPassword, // Send current password for verification
			};

			// Only include new password if it's being changed
			if (formData.newPassword) {
				updateData.password = formData.newPassword;
			}

			await api.put("users/me", updateData, token);

			// Clear password fields
			setFormData((prev) => ({
				...prev,
				currentPassword: "",
				newPassword: "",
				confirmPassword: "",
			}));
		} catch (error) {}
	};

	// Define field configurations
	const emailField = {
		name: "email",
		type: "email",
		placeholder: "Enter your email address",
	};

	const currentPasswordField = {
		name: "currentPassword",
		type: "password",
		placeholder: "Enter your current password",
		helpText: "Required to change your email or password",
		autoComplete: "current-password",
	};

	const newPasswordField = {
		name: "newPassword",
		type: "password",
		placeholder: "Enter new password",
		autoComplete: "new-password",
	};

	const confirmPasswordField = {
		name: "confirmPassword",
		type: "password",
		placeholder: "Confirm new password",
		autoComplete: "new-password",
	};

	return (
		<div className="settings-wrapper">
			<Row className="justify-content-center">
				<Col xl={6} lg={8} md={10}>
					<Card className="settings-card border-0 shadow-sm">
						<Card.Header className="settings-header border-0 p-0">
							<div className="d-flex align-items-center p-4">
								<div className="header-icon-wrapper me-3">
									<i className={`bi ${getTableIcon("user")}`}></i>
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

								{/* Submit Button */}
								<div className="settings-actions">
									<Button variant="primary" type="submit" size="lg" className="save-button w-100">
										<i className="bi bi-check-circle me-2"></i>
										Save Account Changes
									</Button>
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
