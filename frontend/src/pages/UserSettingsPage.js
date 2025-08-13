import React, { useEffect, useState } from "react";
import { Alert, Badge, Button, Card, Col, Container, Form, Row } from "react-bootstrap";
import { useAuth } from "../contexts/AuthContext";
import { useLoading } from "../contexts/LoadingContext";
import { userApi, api } from "../services/Api";
import { isValidTheme, THEMES } from "../utils/Theme";
import { renderFunctions } from "../components/rendering/Renders";

const UserSettingsPage = () => {
	const { currentUser, token } = useAuth();
	const { showLoading, hideLoading } = useLoading();
	const [formData, setFormData] = useState({
		email: "",
		currentPassword: "",
		newPassword: "",
		confirmPassword: "",
		theme: "",
	});
	const [message, setMessage] = useState({ type: "", content: "" });
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

	const validateForm = () => {
		const newErrors = {};

		// Email validation
		if (!formData.email.trim()) {
			newErrors.email = "Email is required";
		} else if (!/\S+@\S+\.\S+/.test(formData.email)) {
			newErrors.email = "Email format is invalid";
		}

		// Password validation (only if changing password)
		if (formData.newPassword || formData.confirmPassword || formData.currentPassword) {
			if (!formData.currentPassword) {
				newErrors.currentPassword = "Current password is required to change password";
			}
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

		showLoading("Updating settings...");
		setMessage({ type: "", content: "" });

		try {
			const updateData = {
				email: formData.email,
				theme: formData.theme,
			};

			// Only include password if it's being changed
			if (formData.newPassword) {
				updateData.password = formData.newPassword;
			}

			// Use the new API structure - calling the /users/me endpoint directly
			const updatedUser = await api.put("users/me", updateData, token);

			// Update theme in document
			document.documentElement.setAttribute("data-theme", formData.theme);
			localStorage.setItem("theme", formData.theme);

			setMessage({
				type: "success",
				content: "Settings updated successfully!",
			});

			// Clear password fields
			setFormData((prev) => ({
				...prev,
				currentPassword: "",
				newPassword: "",
				confirmPassword: "",
			}));

			// Refresh user data to get the updated information
			window.location.reload(); // Simple way to refresh user context
		} catch (error) {
			console.error("Error updating settings:", error);
			setMessage({
				type: "danger",
				content: error.message || "Failed to update settings. Please try again.",
			});
		} finally {
			hideLoading();
		}
	};

	const getThemeDisplay = (themeKey) => {
		const theme = THEMES[themeKey];
		return theme ? theme.name : themeKey;
	};

	const getCurrentCSSColors = (themeKey) => {
		// Temporarily set theme to get colors
		const originalTheme = document.documentElement.getAttribute("data-theme");
		document.documentElement.setAttribute("data-theme", themeKey);

		const computedStyle = getComputedStyle(document.documentElement);
		const colors = {
			start: computedStyle.getPropertyValue("--primary-start").trim(),
			mid: computedStyle.getPropertyValue("--primary-mid").trim(),
			end: computedStyle.getPropertyValue("--primary-end").trim(),
		};

		// Restore original theme
		if (originalTheme) {
			document.documentElement.setAttribute("data-theme", originalTheme);
		}

		return colors;
	};

	const renderColorPreview = (themeKey) => {
		const colors = getCurrentCSSColors(themeKey);
		return (
			<div style={{ display: "flex", alignItems: "center", marginRight: "8px" }}>
				{Object.values(colors).map((color, index) => (
					<div
						key={index}
						style={{
							backgroundColor: color,
							width: "12px",
							height: "12px",
							borderRadius: "50%",
							marginRight: index < 2 ? "3px" : "0",
						}}
					/>
				))}
			</div>
		);
	};

	if (!currentUser) {
		return (
			<Container className="mt-4">
				<Alert variant="info">Loading user information...</Alert>
			</Container>
		);
	}

	return (
		<Container className="mt-4">
			<Row className="justify-content-center">
				<Col md={8} lg={6}>
					<Card>
						<Card.Header>
							<h4 className="mb-0">
								<i className="bi bi-gear me-2"></i>
								User Settings
							</h4>
						</Card.Header>
						<Card.Body>
							{message.content && (
								<Alert
									variant={message.type}
									dismissible
									onClose={() => setMessage({ type: "", content: "" })}
								>
									{message.content}
								</Alert>
							)}

							{/* Account Information */}
							<div className="mb-4">
								<h5 className="text-muted mb-3">
									<i className="bi bi-person-circle me-2"></i>
									Account Information
								</h5>
								<div className="bg-light p-3 rounded">
									<Row>
										<Col sm={4}>
											<strong>Account Created:</strong>
										</Col>
										<Col sm={8}>
											<Badge bg="secondary">{renderFunctions.createdDate(currentUser)}</Badge>
										</Col>
									</Row>
									<Row className="mt-2">
										<Col sm={4}>
											<strong>User ID:</strong>
										</Col>
										<Col sm={8}>
											<Badge bg="info">#{currentUser.id}</Badge>
										</Col>
									</Row>
									{currentUser.is_admin && (
										<Row className="mt-2">
											<Col sm={4}>
												<strong>Role:</strong>
											</Col>
											<Col sm={8}>
												<Badge bg="warning">Administrator</Badge>
											</Col>
										</Row>
									)}
								</div>
							</div>

							<Form onSubmit={handleSubmit}>
								{/* Email Settings */}
								<div className="mb-4">
									<h5 className="text-muted mb-3">
										<i className="bi bi-envelope me-2"></i>
										Email Settings
									</h5>
									<Form.Group className="mb-3">
										<Form.Label>Email Address</Form.Label>
										<Form.Control
											type="email"
											name="email"
											value={formData.email}
											onChange={handleInputChange}
											isInvalid={!!errors.email}
											placeholder="Enter your email"
										/>
										<Form.Control.Feedback type="invalid">{errors.email}</Form.Control.Feedback>
									</Form.Group>
								</div>

								{/* Password Settings */}
								<div className="mb-4">
									<h5 className="text-muted mb-3">
										<i className="bi bi-shield-lock me-2"></i>
										Password Settings
									</h5>
									<div className="text-muted small mb-3">
										<i className="bi bi-info-circle me-1"></i>
										Leave password fields empty if you don't want to change your password.
									</div>

									<Form.Group className="mb-3">
										<Form.Label>Current Password</Form.Label>
										<Form.Control
											type="password"
											name="currentPassword"
											value={formData.currentPassword}
											onChange={handleInputChange}
											isInvalid={!!errors.currentPassword}
											placeholder="Enter current password to change"
										/>
										<Form.Control.Feedback type="invalid">
											{errors.currentPassword}
										</Form.Control.Feedback>
									</Form.Group>

									<Form.Group className="mb-3">
										<Form.Label>New Password</Form.Label>
										<Form.Control
											type="password"
											name="newPassword"
											value={formData.newPassword}
											onChange={handleInputChange}
											isInvalid={!!errors.newPassword}
											placeholder="Enter new password (min. 6 characters)"
										/>
										<Form.Control.Feedback type="invalid">
											{errors.newPassword}
										</Form.Control.Feedback>
									</Form.Group>

									<Form.Group className="mb-3">
										<Form.Label>Confirm New Password</Form.Label>
										<Form.Control
											type="password"
											name="confirmPassword"
											value={formData.confirmPassword}
											onChange={handleInputChange}
											isInvalid={!!errors.confirmPassword}
											placeholder="Confirm your new password"
										/>
										<Form.Control.Feedback type="invalid">
											{errors.confirmPassword}
										</Form.Control.Feedback>
									</Form.Group>
								</div>

								{/* Theme Settings */}
								<div className="mb-4">
									<h5 className="text-muted mb-3">
										<i className="bi bi-palette me-2"></i>
										Theme Settings
									</h5>
									<Form.Group className="mb-3">
										<Form.Label>Application Theme</Form.Label>
										<Form.Select
											name="theme"
											value={formData.theme}
											onChange={handleInputChange}
											isInvalid={!!errors.theme}
										>
											{Object.entries(THEMES).map(([key, theme]) => (
												<option key={key} value={key}>
													{theme.name} - {theme.description}
												</option>
											))}
										</Form.Select>
										<Form.Control.Feedback type="invalid">{errors.theme}</Form.Control.Feedback>
									</Form.Group>

									{/* Theme Preview */}
									<div className="mt-2">
										<small className="text-muted">Preview:</small>
										<div className="d-flex align-items-center mt-1">
											{renderColorPreview(formData.theme)}
											<span className="text-muted">{getThemeDisplay(formData.theme)}</span>
										</div>
									</div>
								</div>

								{/* Submit Button */}
								<div className="d-grid">
									<Button variant="primary" type="submit">
										<i className="bi bi-check-circle me-2"></i>
										Save Settings
									</Button>
								</div>
							</Form>
						</Card.Body>
					</Card>
				</Col>
			</Row>
		</Container>
	);
};

export default UserSettingsPage;
