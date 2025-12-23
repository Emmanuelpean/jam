import React, { useEffect, useState } from "react";
import { Alert, Button, Card, Col, Form, Row } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { authApi, exportApi, userQualificationApi } from "../../services/api/Users";
import { ApiError } from "../../services/api/Base";
import { THEMES } from "../../utils/Theme";
import { FormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import "./UserSettingsPage.css";
import { getTableIcon } from "../../components/rendering/view/Icons";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { findItemByKey } from "../../utils/Utils";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { ValidationErrors } from "../../components/modals/DataModal/DataModal";
import { useFormOptions } from "../../components/rendering/form/FormOptions";
import { UserQualification } from "../../services/Schemas";

interface UserFormData {
	default_currency: string;
	email: string;
	current_password?: string;
	new_password?: string;
	confirm_password?: string;
	chase_threshold?: number;
	deadline_threshold?: number;
	update_limit?: number;
	qualification_id?: number;
	experience?: string;
	skills?: string;
	qualities?: string;
	education?: string;
	interests?: string;
}

const UserSettingsPage: React.FC = () => {
	const { currentUser, token, updateCurrentUser } = useAuth();
	const { currencyNames } = useFormOptions();
	const [formData, setFormData] = useState<UserFormData>(() => ({
		email: currentUser?.email || "",
		chase_threshold: currentUser?.chase_threshold || 0,
		deadline_threshold: currentUser?.deadline_threshold || 0,
		update_limit: currentUser?.update_limit || 0,
		current_password: "",
		new_password: "",
		confirm_password: "",
		default_currency: currentUser?.default_currency || "",
		qualification_id: undefined,
		experience: "",
		skills: "",
		qualities: "",
		education: "",
	}));
	const [activeTab, setActiveTab] = useState<string>("settings");
	const { showToastSuccess, showToastError } = useGlobalToast();
	const [errors, setErrors] = useState<ValidationErrors>({});
	const [submitting, setSubmitting] = useState(false);
	const MIN_PASSWORD_LENGTH: number = parseInt(process.env.MIN_PASSWORD_LENGTH || "8");

	const hasPendingEmail: boolean = !!currentUser?.pending_email && currentUser.pending_email !== currentUser.email;

	// Fetch user qualifications
	useEffect(() => {
		const fetchQualifications = async (): Promise<void> => {
			if (!token) return;
			try {
				const data: UserQualification = await userQualificationApi.getLatest(token);
				if (data) {
					setFormData(
						(prev: UserFormData): UserFormData => ({
							...prev,
							qualification_id: data.id,
							experience: data.experience || "",
							skills: data.skills || "",
							qualities: data.qualities || "",
							education: data.education || "",
							interests: data.interests || "",
						}),
					);
				}
			} catch (error) {
				console.error("Error fetching qualification:", error);
			}
		};

		fetchQualifications().then((_) => null);
	}, [token]);

	useEffect(() => {
		const checkPending = async (): Promise<void> => {
			if (!hasPendingEmail || !token) return;
			try {
				const valid: boolean = await authApi.checkPendingEmail(token);
				if (!valid) {
					showToastError(
						"Pending email verification token has expired. Please request the email change again.",
						"Verification Expired",
					);
				}
			} catch (err) {
				showToastError("Failed to verify pending email status.");
			}
		};
		checkPending().then((_) => null);
	}, [token, hasPendingEmail, showToastError]);

	const downloadJobsExport = async (token: string | null): Promise<void> => {
		if (!token) return;
		try {
			await exportApi.download("jam_export.zip", token);
			showToastSuccess("Data downloaded");
		} catch (e) {
			showToastError("Failed to download data");
		}
	};

	const handleInputChange = (e: SyntheticEvent): void => {
		const { name, value } = e.target;
		setFormData(
			(prev: UserFormData): UserFormData => ({
				...prev,
				[name]: value,
			}),
		);

		if (errors[name]) {
			setErrors(
				(prev: ValidationErrors): ValidationErrors => ({
					...prev,
					[name]: "",
				}),
			);
		}
	};

	const validateForm = (): boolean => {
		const newErrors: ValidationErrors = {};

		const hasAccountChanges: boolean = !!(
			formData.email !== currentUser?.email ||
			formData.new_password ||
			formData.confirm_password
		);

		if (hasAccountChanges && !formData.current_password) {
			newErrors.current_password = "Current password is required to update email or password";
		}

		if (formData.email && !/\S+@\S+\.\S+/.test(formData.email)) {
			newErrors.email = "Email format is invalid";
		}

		if (formData.new_password || formData.confirm_password) {
			if (formData.new_password && formData.new_password.length < MIN_PASSWORD_LENGTH) {
				newErrors.new_password = `New password must be at least ${MIN_PASSWORD_LENGTH} characters long`;
			}
			if (formData.new_password !== formData.confirm_password) {
				newErrors.confirm_password = "Passwords do not match";
			}
		}

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

	const handleSubmitSettings = async (e: React.FormEvent): Promise<void> => {
		e.preventDefault();
		if (!validateForm() || !token) {
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
				default_currency: string;
			} = {
				default_currency: "",
			};

			const emailChanged: boolean = !!(formData.email && formData.email !== currentUser?.email);

			if (formData.current_password) {
				updateData.current_password = formData.current_password;
				if (emailChanged) {
					updateData.email = formData.email;
				}
				if (formData.new_password) {
					updateData.password = formData.new_password;
				}
			}

			if (formData.chase_threshold !== undefined) {
				updateData.chase_threshold = formData.chase_threshold;
			}
			if (formData.deadline_threshold !== undefined) {
				updateData.deadline_threshold = formData.deadline_threshold;
			}
			if (formData.update_limit !== undefined) {
				updateData.update_limit = formData.update_limit;
			}

			updateData.default_currency = formData.default_currency;

			const response = await updateCurrentUser(updateData);

			if (emailChanged) {
				if (response.success) {
					showToastSuccess(response.message, "Email Change Pending");
				} else {
					showToastError(response.message, "Error Updating Settings");
				}
				setFormData((prev) => ({
					...prev,
					email: currentUser?.email || "",
					current_password: "",
				}));
			} else if (response.logged_out) {
				showToastSuccess("Password updated successfully. Please log in again.", "Password Changed");
			} else {
				showToastSuccess("User settings updated successfully.");
			}

			if (formData.new_password) {
				setFormData(
					(prev: UserFormData): UserFormData => ({
						...prev,
						new_password: "",
						confirm_password: "",
					}),
				);
			}
		} catch (error) {
			const apiError = error as ApiError;
			if (apiError.status === 400) {
				showToastError("Email is already in use. Please try a different email.");
			} else if (apiError.status === 401) {
				showToastError("Current password is incorrect. Please try again.");
			} else {
				showToastError("An unknown error occurred. Please try again later.");
			}
		} finally {
			setSubmitting(false);
		}
	};

	const handleQualificationSubmit = async (e: React.FormEvent): Promise<void> => {
		e.preventDefault();
		if (!token) return;

		setSubmitting(true);
		try {
			const qualificationData = {
				id: formData.qualification_id,
				experience: formData.experience || null,
				skills: formData.skills || null,
				qualities: formData.qualities || null,
				education: formData.education || null,
				interests: formData.interests || null,
			};
			await userQualificationApi.upsert(qualificationData, token);
			showToastSuccess("Qualifications saved successfully.");
		} catch (error) {
			console.error("Error saving qualifications:", error);
			showToastError("Failed to save qualifications.");
		} finally {
			setSubmitting(false);
		}
	};

	// Field definitions
	const emailField: ModalFormField = {
		name: "email",
		label: "Email Address",
		type: "text",
		placeholder: "Enter your email address",
		helpText: currentUser?.is_demo
			? `This is a test account. Email changes are disabled.`
			: hasPendingEmail
				? `Email change pending verification. Check ${currentUser?.pending_email} for verification link.`
				: undefined,
		isDisabled: currentUser?.is_demo,
	};

	const currentPasswordField: ModalFormField = {
		name: "current_password",
		type: "password",
		label: "Current Password",
		placeholder: "Enter your current password",
		helpText: currentUser?.is_demo
			? `This is a test account. Email and password changes are disabled.`
			: `Required to change your email or password`,
		isDisabled: currentUser?.is_demo,
	};

	const newPasswordField: ModalFormField = {
		name: "new_password",
		type: "password",
		label: "New Password",
		placeholder: "Enter new password",
		isDisabled: currentUser?.is_demo,
		helpText: currentUser?.is_demo ? `This is a test account. Password changes are disabled.` : null,
	};

	const confirmPasswordField: ModalFormField = {
		name: "confirm_password",
		type: "password",
		label: "Confirm New Password",
		placeholder: "Confirm new password",
		isDisabled: currentUser?.is_demo,
		helpText: currentUser?.is_demo ? `This is a test account. Password changes are disabled.` : null,
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

	const currencyField: ModalFormField = {
		name: "default_currency",
		type: "select",
		label: "Preferred Currency",
		options: currencyNames,
		isClearable: false,
	};

	const experienceField: ModalFormField = {
		name: "experience",
		type: "textarea",
		label: "Experience",
		placeholder: "Describe your work experience...",
		rows: 3,
	};

	const skillsField: ModalFormField = {
		name: "skills",
		type: "textarea",
		label: "Skills",
		placeholder: "List your skills...",
		rows: 3,
	};

	const qualitiesField: ModalFormField = {
		name: "qualities",
		type: "textarea",
		label: "Qualities",
		placeholder: "Describe your qualities...",
		rows: 3,
	};

	const educationField: ModalFormField = {
		name: "education",
		type: "textarea",
		label: "Education",
		placeholder: "Describe your education...",
		rows: 3,
	};

	const interestsField: ModalFormField = {
		name: "interests",
		type: "textarea",
		label: "Interests",
		placeholder: "Describe your interests...",
		rows: 3,
	};

	return (
		<div className="settings-wrapper">
			<Card className="settings-card border-0 shadow-sm">
				<Card.Header className="settings-header border-0 p-0 bg-white">
					<div className="d-flex align-items-center p-4">
						<div className="header-icon-wrapper me-3">
							<i className={`bi ${getTableIcon("User Settings")}`}></i>
						</div>
						<div>
							<h4 className="mb-0 fw-bold text-dark">User Settings</h4>
							<small className="text-muted">Manage your account preferences</small>
						</div>
					</div>
				</Card.Header>

				<div className="custom-tab-nav" style={{ padding: "1rem 1rem" }}>
					<button
						key="settings"
						id="settings-tab"
						type="button"
						className={`custom-tab-button ${activeTab === "settings" ? "active" : ""}`}
						onClick={() => setActiveTab("settings")}
					>
						Settings
					</button>
					<button
						key="qualifications"
						id="qualifications-tab"
						type="button"
						className={`custom-tab-button ${activeTab === "qualifications" ? "active" : ""}`}
						onClick={() => setActiveTab("qualifications")}
					>
						Qualifications
					</button>
				</div>
				<div className="custom-tab-content">
					{activeTab === "settings" && (
						<Card.Body className="p-0">
							<Form onSubmit={handleSubmitSettings} className="p-4">
								{errors.general && <div className="alert alert-danger mb-4">{errors.general}</div>}

								{/* Pending Email Alert */}
								{hasPendingEmail && (
									<Alert variant="warning" className="mb-4">
										<div className="d-flex align-items-start">
											<i className="bi bi-exclamation-triangle-fill me-2 mt-1"></i>
											<div>
												<strong>Email Change Pending</strong>
												<p className="mb-0 mt-1">
													A verification email has been sent to{" "}
													<strong>{currentUser?.pending_email}</strong>. Please check your
													inbox and click the verification link to complete your email change.
												</p>
											</div>
										</div>
									</Alert>
								)}

								<Col md={12} className="mb-3">
									{FormField(currentPasswordField, formData, handleInputChange, errors)}
								</Col>

								{/* Account Settings Section */}
								<div className="settings-section">
									<div className="section-header mb-4">
										<h5 className="section-title">
											<i className="bi bi-envelope me-2 text-primary"></i>
											Account Settings
										</h5>
									</div>
									{FormField(emailField, formData, handleInputChange, errors)}
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
											{FormField(newPasswordField, formData, handleInputChange, errors)}
										</Col>
										<Col md={6} className="mb-3">
											{FormField(confirmPasswordField, formData, handleInputChange, errors)}
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
											{FormField(chaseThresholdField, formData, handleInputChange, errors)}
										</Col>
										<Col md={4} className="mb-3">
											{FormField(deadlineThresholdField, formData, handleInputChange, errors)}
										</Col>
										<Col md={4} className="mb-3">
											{FormField(updateLimitField, formData, handleInputChange, errors)}
										</Col>
									</Row>
								</div>

								{/* Currency Section */}
								<div className="settings-section">
									<div className="section-header mb-4">
										<h5 className="section-title">
											<i className="bi bi-speedometer2 me-2 text-primary"></i>
											Currency Settings
										</h5>
									</div>
									<Row>
										<Col md={12} className="mb-3">
											{FormField(currencyField, formData, handleInputChange, errors)}
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
											{findItemByKey(THEMES, currentUser?.theme)?.name} is not your favourite
											flavour of JAM?! You can easily pick another flavour by clicking on the JAM
											logo in the sidebar.
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
					)}
					{activeTab === "qualifications" && (
						<Card.Body className="p-0">
							<Form onSubmit={handleQualificationSubmit} className="p-4">
								<Col md={12} className="mb-3">
									{FormField(experienceField, formData, handleInputChange, errors)}
								</Col>
								<Col md={12} className="mb-3">
									{FormField(skillsField, formData, handleInputChange, errors)}
								</Col>
								<Col md={12} className="mb-3">
									{FormField(qualitiesField, formData, handleInputChange, errors)}
								</Col>
								<Col md={12} className="mb-3">
									{FormField(educationField, formData, handleInputChange, errors)}
								</Col>
								<Col md={12} className="mb-3">
									{FormField(interestsField, formData, handleInputChange, errors)}
								</Col>
								<div className="settings-actions">
									<div className="horizontal-bar mb-3"></div>
									<ActionButton
										id="confirm-button"
										type="submit"
										disabled={
											submitting ||
											(!formData.experience &&
												!formData.skills &&
												!formData.qualities &&
												!formData.education &&
												!formData.interests)
										}
										loading={submitting}
										className="save-button"
										loadingText="Saving Qualifications..."
										defaultText="Save Qualifications"
										defaultIcon="bi bi-check-circle"
									/>
								</div>
							</Form>
						</Card.Body>
					)}
				</div>
			</Card>
		</div>
	);
};

export default UserSettingsPage;
