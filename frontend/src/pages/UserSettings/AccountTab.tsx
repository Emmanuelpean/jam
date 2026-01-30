import React, { JSX, useEffect, useState } from "react";
import { Alert, Col, Form, Modal, Row } from "react-bootstrap";
import { ValidationErrors } from "../../components/DataModal/DataModal";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAuth } from "../../contexts/AuthContext";
import { authApi, exportApi, GenericResponse, UpdateCurrentUserResponse } from "../../services/api/Users";
import { ApiResponse } from "../../services/api/Base";
import { renderFormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { useNavigate } from "react-router-dom";
import { useConfig } from "../../contexts/ConfigContext";

interface AccountFormData {
	email?: string;
	current_password?: string;
	new_password?: string;
	confirm_password?: string;
	first_name?: string;
	last_name?: string;
	delete_password?: string;
}

export const AccountTab: React.FC = (): JSX.Element => {
	const { config } = useConfig();
	const { currentUser, token, updateCurrentUser, logout } = useAuth();
	const { showToastSuccess, showToastError, showApiError } = useGlobalToast();
	const navigate = useNavigate();
	const [formData, setFormData] = useState<AccountFormData>(() => ({
		email: currentUser?.email || "",
		current_password: "",
		new_password: "",
		confirm_password: "",
		first_name: currentUser?.first_name || "",
		last_name: currentUser?.last_name || "",
		delete_password: "",
	}));
	const [errors, setErrors] = useState<ValidationErrors>({});
	const [submitting, setSubmitting] = useState(false);
	const [showDeleteModal, setShowDeleteModal] = useState(false);
	const [showConfirmModal, setShowConfirmModal] = useState(false);
	const [deleting, setDeleting] = useState(false);
	const [downloadingData, setDownloadingData] = useState(false);
	const hasPendingEmail: boolean = !!currentUser?.pending_email_change;

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

	const proceedToConfirmation = (): void => {
		if (!formData.delete_password) return;
		setShowDeleteModal(false);
		setShowConfirmModal(true);
	};

	const closeConfirmModal = (): void => {
		setShowConfirmModal(false);
		setFormData((prev: AccountFormData): AccountFormData => ({ ...prev, delete_password: "" }));
	};

	const handleInputChange = (e: SyntheticEvent): void => {
		const { name, value } = e.target;
		setFormData((prev: AccountFormData): AccountFormData => ({ ...prev, [name]: value }));
		if (errors[name]) {
			setErrors((prev: ValidationErrors): ValidationErrors => ({ ...prev, [name]: "" }));
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
			if (formData.new_password && formData.new_password.length < config.min_password_length) {
				newErrors.new_password = `New password must be at least ${config.min_password_length} characters long`;
			}
			if (formData.new_password !== formData.confirm_password) {
				newErrors.confirm_password = "Passwords do not match";
			}
		}

		setErrors(newErrors);
		return Object.keys(newErrors).length === 0;
	};

	const handleSubmit = async (e: React.FormEvent): Promise<void> => {
		e.preventDefault();
		if (!validateForm() || !token) return;
		setSubmitting(true);

		try {
			const updateData: any = {};
			const emailChanged: boolean = !!(formData.email && formData.email !== currentUser?.email);

			if (formData.current_password) {
				updateData.current_password = formData.current_password;
				if (emailChanged) updateData.email = formData.email;
				if (formData.new_password) updateData.password = formData.new_password;
			}

			if (formData.first_name !== undefined) updateData.first_name = formData.first_name;
			if (formData.last_name !== undefined) updateData.last_name = formData.last_name;

			const response: ApiResponse<UpdateCurrentUserResponse> | null = await updateCurrentUser(updateData);
			if (!response) return;

			const responseData: UpdateCurrentUserResponse = response.data;

			if (emailChanged) {
				if (responseData.success) {
					showToastSuccess(responseData.message, "Email Change Pending");
					setFormData(
						(prev: AccountFormData): AccountFormData => ({
							...prev,
							email: currentUser?.email || "",
							current_password: "",
						})
					);
				} else {
					showToastError(responseData.message, "Error Updating Settings");
				}
			} else if (responseData.logged_out) {
				showToastSuccess("Password updated successfully. Please log in again.", "Password Changed");
			} else {
				showToastSuccess("Account settings updated successfully.");
			}

			if (formData.new_password) {
				setFormData(
					(prev: AccountFormData): AccountFormData => ({
						...prev,
						new_password: "",
						confirm_password: "",
						current_password: "",
					})
				);
			}
		} catch (error) {
			showApiError(
				error,
				"Account Update Failed",
				"An unknown error occured while trying to update your account details."
			);
		} finally {
			setSubmitting(false);
		}
	};

	const emailField: ModalFormField = {
		name: "email",
		label: "Email Address",
		type: "text",
		placeholder: "Enter your email address",
		helpText: currentUser?.is_demo
			? "This is a test account. Email changes are disabled."
			: hasPendingEmail
				? `Email change pending verification. Check ${currentUser?.pending_email_change} for verification link.`
				: undefined,
		isDisabled: currentUser?.is_demo,
	};

	const currentPasswordField: ModalFormField = {
		name: "current_password",
		type: "password",
		label: "Current Password",
		placeholder: "Enter your current password",
		helpText: currentUser?.is_demo
			? "This is a test account. Email and password change are disabled."
			: "Required to change your email or password",
		isDisabled: currentUser?.is_demo,
	};

	const newPasswordField: ModalFormField = {
		name: "new_password",
		type: "password",
		label: "New Password",
		placeholder: "Enter new password",
		isDisabled: currentUser?.is_demo,
		helpText: currentUser?.is_demo ? "This is a test account. Password change is disabled." : null,
	};

	const confirmPasswordField: ModalFormField = {
		name: "confirm_password",
		type: "password",
		label: "Confirm New Password",
		placeholder: "Confirm new password",
		isDisabled: currentUser?.is_demo,
		helpText: currentUser?.is_demo ? "This is a test account. Password change is disabled." : null,
	};

	const firstNameField: ModalFormField = {
		name: "first_name",
		type: "text",
		label: "First Name",
		placeholder: "Enter your first name",
	};

	const lastNameField: ModalFormField = {
		name: "last_name",
		type: "text",
		label: "Last Name",
		placeholder: "Enter your last name",
	};

	const deletePasswordField: ModalFormField = {
		name: "delete_password",
		type: "password",
		label: "Password",
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
			{renderFormField(emailField, formData, handleInputChange, errors)}

			<hr className="my-4" />

			<h5 className="mb-3">
				<i className="bi bi-lock"></i> Security
			</h5>
			{renderFormField(currentPasswordField, formData, handleInputChange, errors)}
			<Row>
				<Col md={6}>{renderFormField(newPasswordField, formData, handleInputChange, errors)}</Col>
				<Col md={6}>{renderFormField(confirmPasswordField, formData, handleInputChange, errors)}</Col>
			</Row>

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

			<div className="mt-4">
				<ActionButton
					type="submit"
					variant="primary"
					disabled={submitting}
					defaultIcon="bi-save"
					id={"confirm-button"}
					defaultText={"Save Account Settings"}
					loadingText={"Saving..."}
				/>
			</div>

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

			<Modal show={showDeleteModal} onHide={closeDeleteModal} size={"lg"} centered id="delete-account-modal">
				<Modal.Header closeButton>
					<Modal.Title>
						<i className="bi bi-exclamation-triangle"></i> Delete Account
					</Modal.Title>
				</Modal.Header>
				<Modal.Body>
					<Alert variant="danger">
						<strong>Warning:</strong> This action is permanent and cannot be undone. All your data will be
						permanently deleted.
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
						disabled={!formData.delete_password}
						defaultIcon="bi-arrow-right"
						defaultText="Continue"
						id="continue-delete-button"
					/>
				</Modal.Footer>
			</Modal>

			<Modal show={showConfirmModal} onHide={closeConfirmModal} size={"lg"} centered id="confirm-delete-modal">
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
							<li>Saved jobs and email alerts</li>
							<li>User preferences and settings</li>
							<li>Interview records and notes</li>
							<li>All contacts and companies</li>
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
			</Modal>
		</Form>
	);
};
