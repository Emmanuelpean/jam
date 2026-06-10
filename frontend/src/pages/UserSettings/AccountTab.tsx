import React, { JSX, useEffect, useRef, useState } from "react";
import { Alert, Col, Form, Modal, Row } from "react-bootstrap";
import JamModal from "../../components/JamModal/JamModal";
import { ValidationErrors } from "../../components/DataModal/DataModal";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAuth } from "../../contexts/AuthContext";
import { authApi, exportApi, GenericResponse } from "../../services/api/Users";
import { ApiResponse } from "../../services/api/Base";
import { ApiError, handleApiError } from "../../services/api/ApiError";
import { renderFormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { EmailValidation, ModalFormField } from "../../components/rendering/form/FormRenders";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { useNavigate } from "react-router-dom";
import { useConfig } from "../../contexts/ConfigContext";

interface AccountFormData {
	first_name?: string;
	last_name?: string;
	delete_password?: string;
}

interface EmailFormData {
	email?: string;
}

interface PasswordFormData {
	current_password?: string;
	new_password?: string;
	confirm_password?: string;
}

export const AccountTab: React.FC = (): JSX.Element => {
	const { config } = useConfig();
	const { currentUser, token, updateCurrentUser, fetchUserInfo, logout } = useAuth();
	const { showToastSuccess, showToastError, showApiError } = useGlobalToast();
	const navigate = useNavigate();
	const [formData, setFormData] = useState<AccountFormData>(() => ({
		first_name: currentUser?.first_name || "",
		last_name: currentUser?.last_name || "",
		delete_password: "",
	}));
	const [errors, setErrors] = useState<ValidationErrors>({});
	const [submitting, setSubmitting] = useState(false);
	const [showDeleteModal, setShowDeleteModal] = useState(false);
	const formInitialized = useRef(false);

	useEffect(() => {
		if (currentUser && !formInitialized.current) {
			formInitialized.current = true;
			setFormData((prev) => ({
				...prev,
				first_name: currentUser.first_name || "",
				last_name: currentUser.last_name || "",
			}));
		}
	}, [currentUser]);
	const [showConfirmModal, setShowConfirmModal] = useState(false);
	const [verifying, setVerifying] = useState(false);
	const [deleting, setDeleting] = useState(false);
	const [downloadingData, setDownloadingData] = useState(false);
	const hasPendingEmail: boolean = !!currentUser?.pending_email_change;

	// Email change modal
	const [showEmailModal, setShowEmailModal] = useState(false);
	const [emailFormData, setEmailFormData] = useState<EmailFormData>({ email: "" });
	const [emailErrors, setEmailErrors] = useState<ValidationErrors>({});
	const [changingEmail, setChangingEmail] = useState(false);

	// Password change modal
	const [showPasswordModal, setShowPasswordModal] = useState(false);
	const [passwordFormData, setPasswordFormData] = useState<PasswordFormData>({
		current_password: "",
		new_password: "",
		confirm_password: "",
	});
	const [passwordErrors, setPasswordErrors] = useState<ValidationErrors>({});
	const [changingPassword, setChangingPassword] = useState(false);

	useEffect(() => {
		const checkPending = async (): Promise<void> => {
			if (!hasPendingEmail || !token) return;
			try {
				const valid: ApiResponse<boolean> = await authApi.checkPendingEmail(token);
				if (!valid.data) {
					showToastError(
						"Pending email verification token has expired. Please request the email change again.",
						"Verification Expired"
					);
				}
			} catch (error) {
				showApiError(error, "Pending email check", "Failed to verify pending email status.");
			}
		};
		checkPending().then((): void => {});
	}, [token, hasPendingEmail, showToastError]);

	const downloadJobsExport = async (): Promise<void> => {
		if (!token) return;
		setDownloadingData(true);
		try {
			await exportApi.download("jam_export.zip", token);
			showToastSuccess("Data downloaded");
		} catch (error) {
			showApiError(error, "Download Failed", "An unknown error occurred while downloading the data.");
		} finally {
			setDownloadingData(false);
		}
	};

	const handleDeleteAccount = async (): Promise<void> => {
		if (!formData.delete_password) return;
		if (!token) return;
		setDeleting(true);

		try {
			const response: ApiResponse<GenericResponse> = await authApi.deleteAccount(formData.delete_password, token);
			if (response.data.success) {
				showToastSuccess("Your account has been permanently deleted.", "Account Deleted");
				logout();
				navigate("/");
			}
		} catch (error) {
			showApiError(error, "Account Deletion Failed", "Failed to delete your account due to an unknown error");
		} finally {
			setDeleting(false);
		}
	};

	const openDeleteModal = (): void => {
		setShowDeleteModal(true);
		setFormData((prev: AccountFormData): AccountFormData => ({ ...prev, delete_password: "" }));
	};

	const closeDeleteModal = (): void => {
		setShowDeleteModal(false);
		setFormData((prev: AccountFormData): AccountFormData => ({ ...prev, delete_password: "" }));
	};

	const proceedToConfirmation = async (): Promise<void> => {
		if (!formData.delete_password || !token) return;
		setVerifying(true);
		try {
			await authApi.verifyPassword(formData.delete_password, token);
			setShowDeleteModal(false);
			setShowConfirmModal(true);
		} catch (error) {
			setErrors(
				(prev: ValidationErrors): ValidationErrors => ({ ...prev, delete_password: "Password is incorrect." })
			);
		} finally {
			setVerifying(false);
		}
	};

	const closeConfirmModal = (): void => {
		setShowConfirmModal(false);
		setFormData((prev: AccountFormData): AccountFormData => ({ ...prev, delete_password: "" }));
	};

	const handleInputChange = (e: SyntheticEvent): void => {
		const { name, value } = e.target;
		setFormData((prev: AccountFormData): AccountFormData => ({ ...prev, [name]: value }));
		setErrors((prev: ValidationErrors): ValidationErrors => {
			const next = { ...prev };
			if (next[name]) delete next[name];
			return next;
		});
	};

	const handleEmailInputChange = (e: SyntheticEvent): void => {
		const { name, value } = e.target;
		setEmailFormData((prev: EmailFormData): EmailFormData => ({ ...prev, [name]: value }));
		setEmailErrors((prev: ValidationErrors): ValidationErrors => {
			const next = { ...prev };
			if (next[name]) delete next[name];
			return next;
		});
	};

	const handlePasswordInputChange = (e: SyntheticEvent): void => {
		const { name, value } = e.target;
		setPasswordFormData((prev: PasswordFormData): PasswordFormData => ({ ...prev, [name]: value }));
		setPasswordErrors((prev: ValidationErrors): ValidationErrors => {
			const next = { ...prev };
			if (next[name]) delete next[name];
			if (name === "new_password" && next.confirm_password) delete next.confirm_password;
			return next;
		});
	};

	const handleSubmit = async (e: React.FormEvent): Promise<void> => {
		e.preventDefault();
		if (!token) return;
		setSubmitting(true);

		try {
			await updateCurrentUser({
				first_name: formData.first_name,
				last_name: formData.last_name,
			});
			showToastSuccess("Account settings updated successfully.");
		} catch (error) {
			showApiError(
				error,
				"Account Update Failed",
				"An unknown error occurred while trying to update your account details."
			);
		} finally {
			setSubmitting(false);
		}
	};

	// ----- Email change modal handlers -----

	const openEmailModal = (): void => {
		setEmailFormData({ email: "" });
		setEmailErrors({});
		setShowEmailModal(true);
	};

	const closeEmailModal = (): void => {
		setShowEmailModal(false);
		setEmailFormData({ email: "" });
		setEmailErrors({});
	};

	const handleEmailSubmit = async (): Promise<void> => {
		if (!token) return;
		const newEmail = (emailFormData.email || "").trim();
		const validationError = newEmail ? EmailValidation(newEmail) : "Email is required";
		if (validationError) {
			setEmailErrors({ email: validationError });
			return;
		}
		if (newEmail === currentUser?.email) {
			setEmailErrors({ email: "New email must be different from your current email." });
			return;
		}

		setChangingEmail(true);
		try {
			await authApi.updateEmail(newEmail, token);
			const message = `A verification email has been sent to ${newEmail}. Please check your inbox to confirm the change.`;
			showToastSuccess(message, "Email Change Pending");
			await fetchUserInfo(token);
			closeEmailModal();
		} catch (error) {
			const { status } = handleApiError(error);
			const detail =
				error instanceof ApiError ? (error.data as { detail?: string } | undefined)?.detail : undefined;
			if ((status === 400 || status === 429) && detail) {
				setEmailErrors({ email: detail });
			} else {
				showApiError(
					error,
					"Email Change Failed",
					"An unknown error occurred while trying to change your email."
				);
			}
		} finally {
			setChangingEmail(false);
		}
	};

	// ----- Password change modal handlers -----

	const openPasswordModal = (): void => {
		setPasswordFormData({ current_password: "", new_password: "", confirm_password: "" });
		setPasswordErrors({});
		setShowPasswordModal(true);
	};

	const closePasswordModal = (): void => {
		setShowPasswordModal(false);
		setPasswordFormData({ current_password: "", new_password: "", confirm_password: "" });
		setPasswordErrors({});
	};

	const validatePasswordForm = (): boolean => {
		const newErrors: ValidationErrors = {};
		if (!passwordFormData.current_password) {
			newErrors.current_password = "Current password is required";
		}
		if (!passwordFormData.new_password) {
			newErrors.new_password = "New password is required";
		} else if (passwordFormData.new_password.length < config.min_password_length) {
			newErrors.new_password = `New password must be at least ${config.min_password_length} characters long`;
		}
		if (passwordFormData.new_password !== passwordFormData.confirm_password) {
			newErrors.confirm_password = "Passwords do not match";
		}
		setPasswordErrors(newErrors);
		return Object.keys(newErrors).length === 0;
	};

	const handlePasswordSubmit = async (): Promise<void> => {
		if (!token) return;
		if (!validatePasswordForm()) return;

		setChangingPassword(true);
		try {
			await authApi.updatePassword(
				{
					current_password: passwordFormData.current_password || "",
					new_password: passwordFormData.new_password || "",
				},
				token
			);
			showToastSuccess("Password has been successfully updated. Please log in again.", "Password Changed");
			closePasswordModal();
			logout();
		} catch (error) {
			const { status } = handleApiError(error);
			const detail =
				error instanceof ApiError ? (error.data as { detail?: string } | undefined)?.detail : undefined;
			if (status === 401) {
				setPasswordErrors({ current_password: "The current password is incorrect." });
			} else if (status === 429 && detail) {
				setPasswordErrors({ current_password: detail });
			} else {
				showApiError(
					error,
					"Password Update Failed",
					"An unknown error occurred while trying to update your password."
				);
			}
		} finally {
			setChangingPassword(false);
		}
	};

	// ----- Field definitions -----

	const firstNameField: ModalFormField = {
		key: "first_name",
		type: "text",
		label: "First Name",
		placeholder: "Enter your first name",
	};

	const lastNameField: ModalFormField = {
		key: "last_name",
		type: "text",
		label: "Last Name",
		placeholder: "Enter your last name",
	};

	const newEmailField: ModalFormField = {
		key: "email",
		type: "text",
		label: "New Email Address",
		placeholder: "Enter your new email address",
		autoComplete: "email",
		isDisabled: changingEmail,
	};

	const currentPasswordField: ModalFormField = {
		key: "current_password",
		type: "password",
		label: "Current Password",
		placeholder: "Enter your current password",
		autoComplete: "current-password",
		isDisabled: changingPassword,
	};

	const newPasswordField: ModalFormField = {
		key: "new_password",
		type: "password",
		label: "New Password",
		placeholder: "Enter new password",
		autoComplete: "new-password",
		isDisabled: changingPassword,
	};

	const confirmPasswordField: ModalFormField = {
		key: "confirm_password",
		type: "password",
		label: "Confirm New Password",
		placeholder: "Confirm new password",
		autoComplete: "new-password",
		isDisabled: changingPassword,
	};

	const deletePasswordField: ModalFormField = {
		key: "delete_password",
		type: "password",
		label: "Password",
		isDisabled: verifying,
	};

	return (
		<Form onSubmit={handleSubmit}>
			{errors.general && <Alert variant="danger">{errors.general}</Alert>}

			{hasPendingEmail && (
				<Alert variant="info" id={"pending-email-info"}>
					<Alert.Heading>Email Change Pending</Alert.Heading>A verification email has been sent to{" "}
					<strong>{currentUser?.pending_email_change}</strong>. Please check your inbox and click the
					verification link to complete your email change.
				</Alert>
			)}

			<h5 className="mb-3">
				<i className="bi bi-person"></i> Personal Information
			</h5>
			<Row>
				<Col md={6}>{renderFormField(firstNameField, formData, handleInputChange, errors)}</Col>
				<Col md={6}>{renderFormField(lastNameField, formData, handleInputChange, errors)}</Col>
			</Row>
			<div className="mt-3">
				<ActionButton
					type="submit"
					variant="primary"
					disabled={submitting}
					loading={submitting}
					defaultIcon="bi-save"
					id={"confirm-button"}
					defaultText={"Save Account Settings"}
					loadingText={"Saving..."}
				/>
			</div>

			<hr className="my-4" />

			<h5 className="mb-3">
				<i className="bi bi-lock"></i> Security
			</h5>
			<Row className="align-items-center mb-3">
				<Col md={4} className="fw-semibold">
					Email Address
				</Col>
				<Col md={5} className="text-muted">
					{currentUser?.email}
				</Col>
				<Col md={3} className="text-md-end">
					<ActionButton
						variant="outline-primary"
						onClick={openEmailModal}
						defaultIcon="bi-envelope"
						defaultText="Change Email"
						disabled={currentUser?.is_demo}
						id="change-email-button"
					/>
				</Col>
			</Row>
			<Row className="align-items-center">
				<Col md={4} className="fw-semibold">
					Password
				</Col>
				<Col md={5} className="text-muted">
					••••••••
				</Col>
				<Col md={3} className="text-md-end">
					<ActionButton
						variant="outline-primary"
						onClick={openPasswordModal}
						defaultIcon="bi-key"
						defaultText="Change Password"
						disabled={currentUser?.is_demo}
						id="change-password-button"
					/>
				</Col>
			</Row>
			{currentUser?.is_demo && (
				<p className="text-muted mt-2">
					<small>This is a test account. Email and password changes are disabled.</small>
				</p>
			)}

			<hr className="my-4" />

			<h5 className="mb-3">
				<i className="bi bi-download"></i> Data Export
			</h5>
			<p className="text-muted">Download all your job application data</p>
			<ActionButton
				variant="secondary"
				onClick={downloadJobsExport}
				disabled={downloadingData}
				loading={downloadingData}
				defaultIcon={"bi-download"}
				defaultText={"Download Data"}
				loadingText={"Downloading..."}
				id="download-data-button"
			/>

			<hr className="my-4" />

			<h5 className="mb-3 text-danger">
				<i className="bi bi-exclamation-triangle text-danger"></i> Danger Zone
			</h5>
			<p className="text-muted">
				Permanently delete your account and all associated data. This action cannot be undone.
			</p>
			<ActionButton
				variant="danger"
				onClick={openDeleteModal}
				defaultIcon="bi-trash"
				defaultText="Delete Account"
				disabled={currentUser?.is_demo}
				id="delete-account-button"
			/>
			{currentUser?.is_demo && (
				<p className="text-muted mt-2">
					<small>This is a test account. Account deletion is disabled.</small>
				</p>
			)}

			{/* ----- Change Email modal ----- */}
			<JamModal show={showEmailModal} onHide={closeEmailModal} size={"lg"} centered id="change-email-modal">
				<Modal.Header closeButton>
					<Modal.Title>
						<i className="bi bi-envelope"></i> Change Email Address
					</Modal.Title>
				</Modal.Header>
				<Form
					onSubmit={(e) => {
						e.preventDefault();
						e.stopPropagation();
						void handleEmailSubmit();
					}}
				>
					<Modal.Body>
						<p className="text-muted">
							We'll send a verification link to the new email address. The change only takes effect once
							you click that link.
						</p>
						<p>
							Current email: <strong>{currentUser?.email}</strong>
						</p>
						{renderFormField(newEmailField, emailFormData, handleEmailInputChange, emailErrors)}
					</Modal.Body>
					<Modal.Footer>
						<ActionButton
							variant="secondary"
							onClick={closeEmailModal}
							defaultText="Cancel"
							disabled={changingEmail}
							id="cancel-email-change-button"
						/>
						<ActionButton
							type="submit"
							variant="primary"
							disabled={changingEmail}
							loading={changingEmail}
							defaultIcon="bi-send"
							defaultText="Send Verification Email"
							loadingText="Sending..."
							id="confirm-email-change-button"
						/>
					</Modal.Footer>
				</Form>
			</JamModal>

			{/* ----- Change Password modal ----- */}
			<JamModal
				show={showPasswordModal}
				onHide={closePasswordModal}
				size={"lg"}
				centered
				id="change-password-modal"
			>
				<Modal.Header closeButton>
					<Modal.Title>
						<i className="bi bi-key"></i> Change Password
					</Modal.Title>
				</Modal.Header>
				<Form
					onSubmit={(e) => {
						e.preventDefault();
						e.stopPropagation();
						void handlePasswordSubmit();
					}}
				>
					<Modal.Body>
						<p className="text-muted">
							Once your password is updated, you'll be logged out and will need to sign in again with the
							new password.
						</p>
						{renderFormField(
							currentPasswordField,
							passwordFormData,
							handlePasswordInputChange,
							passwordErrors
						)}
						<Row>
							<Col md={6}>
								{renderFormField(
									newPasswordField,
									passwordFormData,
									handlePasswordInputChange,
									passwordErrors
								)}
							</Col>
							<Col md={6}>
								{renderFormField(
									confirmPasswordField,
									passwordFormData,
									handlePasswordInputChange,
									passwordErrors
								)}
							</Col>
						</Row>
					</Modal.Body>
					<Modal.Footer>
						<ActionButton
							variant="secondary"
							onClick={closePasswordModal}
							defaultText="Cancel"
							disabled={changingPassword}
							id="cancel-password-change-button"
						/>
						<ActionButton
							type="submit"
							variant="primary"
							disabled={changingPassword}
							loading={changingPassword}
							defaultIcon="bi-check2"
							defaultText="Update Password"
							loadingText="Updating..."
							id="confirm-password-change-button"
						/>
					</Modal.Footer>
				</Form>
			</JamModal>

			<JamModal show={showDeleteModal} onHide={closeDeleteModal} size={"lg"} centered id="delete-account-modal">
				<Modal.Header closeButton>
					<Modal.Title>
						<i className="bi bi-exclamation-triangle"></i> Delete Account
					</Modal.Title>
				</Modal.Header>
				<Form
					onSubmit={(e) => {
						e.preventDefault();
						e.stopPropagation();
						void proceedToConfirmation();
					}}
				>
					<Modal.Body>
						<Alert variant="danger">
							<strong>Warning:</strong> This action is permanent and cannot be undone. All your data will
							be permanently deleted.
						</Alert>
						<p>Please enter your password to confirm account deletion:</p>
						{renderFormField(deletePasswordField, formData, handleInputChange, errors)}
					</Modal.Body>
					<Modal.Footer>
						<ActionButton
							variant="secondary"
							onClick={closeDeleteModal}
							defaultText="Cancel"
							id="cancel-delete-button"
						/>
						<ActionButton
							variant="danger"
							onClick={proceedToConfirmation}
							disabled={!formData.delete_password || verifying}
							loading={verifying}
							defaultIcon="bi-arrow-right"
							defaultText="Continue"
							loadingText="Verifying..."
							id="continue-delete-button"
						/>
					</Modal.Footer>
				</Form>
			</JamModal>

			<JamModal show={showConfirmModal} onHide={closeConfirmModal} size={"lg"} centered id="confirm-delete-modal">
				<Modal.Header closeButton>
					<Modal.Title>
						<i className="bi bi-exclamation-triangle-fill"></i> Final Confirmation
					</Modal.Title>
				</Modal.Header>
				<Modal.Body>
					<Alert variant="danger">
						<Alert.Heading>Are you absolutely sure?</Alert.Heading>
						<p className="mb-0">
							This will permanently delete your account and all associated data including:
						</p>
						<ul className="mt-2 mb-0">
							<li>All job applications and tracking data</li>
							<li>Interview records and job application updates</li>
							<li>All contact and company records</li>
							<li>User preferences and settings</li>
							<li>Saved jobs and email alerts</li>
							{currentUser?.premium?.is_active && (
								<li className="fw-bold">
									Your active premium subscription (will be cancelled immediately)
								</li>
							)}
						</ul>
					</Alert>
					<Alert variant="info">
						<Alert.Heading className="h6">
							<i className="bi bi-download"></i> Download Your Data
						</Alert.Heading>
						<p className="mb-2">
							Before you delete your account, you may want to download a copy of your data for your
							records.
						</p>
						<ActionButton
							variant="primary"
							onClick={downloadJobsExport}
							disabled={downloadingData}
							loading={downloadingData}
							defaultIcon={"bi-download"}
							defaultText={"Download My Data"}
							loadingText={"Downloading..."}
							id="download-data-modal-button"
						/>
					</Alert>
				</Modal.Body>
				<Modal.Footer>
					<ActionButton
						variant="secondary"
						onClick={closeConfirmModal}
						defaultText="Cancel"
						id="cancel-confirm-delete-button"
					/>
					<ActionButton
						variant="danger"
						onClick={handleDeleteAccount}
						disabled={deleting}
						defaultIcon={"bi-trash"}
						defaultText={deleting ? "Deleting..." : "Yes, Delete My Account"}
						id="final-delete-button"
					/>
				</Modal.Footer>
			</JamModal>
		</Form>
	);
};
