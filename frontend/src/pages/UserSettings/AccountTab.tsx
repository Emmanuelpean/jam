import React, { useEffect, useState } from "react";
import { Alert, Col, Row, Form } from "react-bootstrap";
import { ValidationErrors } from "../../components/modals/DataModal/DataModal";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAuth } from "../../contexts/AuthContext";
import { authApi, exportApi, UpdateCurrentUserResponse } from "../../services/api/Users";
import { ApiError, ApiResponse } from "../../services/api/Base";
import { FormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { ActionButton } from "../../components/rendering/form/ActionButton";

interface AccountFormData {
	email: string;
	current_password?: string;
	new_password?: string;
	confirm_password?: string;
	first_name?: string;
	last_name?: string;
}

export const AccountTab: React.FC = () => {
	const { currentUser, token, updateCurrentUser } = useAuth();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const [formData, setFormData] = useState<AccountFormData>(() => ({
		email: currentUser?.email || "",
		current_password: "",
		new_password: "",
		confirm_password: "",
		first_name: currentUser?.first_name || "",
		last_name: currentUser?.last_name || "",
	}));
	const [errors, setErrors] = useState<ValidationErrors>({});
	const [submitting, setSubmitting] = useState(false);
	const MIN_PASSWORD_LENGTH = parseInt(process.env.MIN_PASSWORD_LENGTH || "8");
	const hasPendingEmail = !!currentUser?.pending_email && currentUser.pending_email !== currentUser.email;

	useEffect(() => {
		const checkPending = async () => {
			if (!hasPendingEmail || !token) return;
			try {
				const valid: ApiResponse<boolean> = await authApi.checkPendingEmail(token);
				if (!valid.data) {
					showToastError(
						"Pending email verification token has expired. Please request the email change again.",
						"Verification Expired",
					);
				}
			} catch (err) {
				showToastError("Failed to verify pending email status.");
			}
		};
		checkPending();
	}, [token, hasPendingEmail, showToastError]);

	const downloadJobsExport = async (token: string | null) => {
		if (!token) return;
		try {
			await exportApi.download("jam_export.zip", token);
			showToastSuccess("Data downloaded");
		} catch (e) {
			showToastError("Failed to download data");
		}
	};

	const handleInputChange = (e: SyntheticEvent) => {
		const { name, value } = e.target;
		setFormData((prev) => ({ ...prev, [name]: value }));
		if (errors[name]) {
			setErrors((prev) => ({ ...prev, [name]: "" }));
		}
	};

	const validateForm = (): boolean => {
		const newErrors: ValidationErrors = {};
		const hasAccountChanges = !!(
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

		setErrors(newErrors);
		return Object.keys(newErrors).length === 0;
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!validateForm() || !token) return;
		setSubmitting(true);

		try {
			const updateData: any = {};
			const emailChanged = !!(formData.email && formData.email !== currentUser?.email);

			if (formData.current_password) {
				updateData.current_password = formData.current_password;
				if (emailChanged) updateData.email = formData.email;
				if (formData.new_password) updateData.password = formData.new_password;
			}

			if (formData.first_name !== undefined) updateData.first_name = formData.first_name;
			if (formData.last_name !== undefined) updateData.last_name = formData.last_name;

			const response: ApiResponse<UpdateCurrentUserResponse> | null = await updateCurrentUser(updateData);
			if (!response) return;

			const responseData = response.data;

			if (emailChanged) {
				if (responseData.success) {
					showToastSuccess(responseData.message, "Email Change Pending");
					setFormData((prev) => ({ ...prev, email: currentUser?.email || "", current_password: "" }));
				} else {
					showToastError(responseData.message, "Error Updating Settings");
				}
			} else if (responseData.logged_out) {
				showToastSuccess("Password updated successfully. Please log in again.", "Password Changed");
			} else {
				showToastSuccess("Account settings updated successfully.");
			}

			if (formData.new_password) {
				setFormData((prev) => ({
					...prev,
					new_password: "",
					confirm_password: "",
					current_password: "",
				}));
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

	const emailField: ModalFormField = {
		name: "email",
		label: "Email Address",
		type: "text",
		placeholder: "Enter your email address",
		helpText: currentUser?.is_demo
			? "This is a test account. Email changes are disabled."
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
			? "This is a test account. Email and password changes are disabled."
			: "Required to change your email or password",
		isDisabled: currentUser?.is_demo,
	};

	const newPasswordField: ModalFormField = {
		name: "new_password",
		type: "password",
		label: "New Password",
		placeholder: "Enter new password",
		isDisabled: currentUser?.is_demo,
		helpText: currentUser?.is_demo ? "This is a test account. Password changes are disabled." : null,
	};

	const confirmPasswordField: ModalFormField = {
		name: "confirm_password",
		type: "password",
		label: "Confirm New Password",
		placeholder: "Confirm new password",
		isDisabled: currentUser?.is_demo,
		helpText: currentUser?.is_demo ? "This is a test account. Password changes are disabled." : null,
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

	return (
		<Form onSubmit={handleSubmit}>
			{errors.general && <Alert variant="danger">{errors.general}</Alert>}

			{hasPendingEmail && (
				<Alert variant="info">
					<Alert.Heading>Email Change Pending</Alert.Heading>A verification email has been sent to{" "}
					<strong>{currentUser?.pending_email}</strong>. Please check your inbox and click the verification
					link to complete your email change.
				</Alert>
			)}

			<h5 className="mb-3">
				<i className="bi bi-person"></i> Personal Information
			</h5>
			<Row>
				<Col md={6}>{FormField(firstNameField, formData, handleInputChange, errors)}</Col>
				<Col md={6}>{FormField(lastNameField, formData, handleInputChange, errors)}</Col>
			</Row>
			{FormField(emailField, formData, handleInputChange, errors)}

			<hr className="my-4" />

			<h5 className="mb-3">
				<i className="bi bi-lock"></i> Security
			</h5>
			{FormField(currentPasswordField, formData, handleInputChange, errors)}
			<Row>
				<Col md={6}>{FormField(newPasswordField, formData, handleInputChange, errors)}</Col>
				<Col md={6}>{FormField(confirmPasswordField, formData, handleInputChange, errors)}</Col>
			</Row>

			<hr className="my-4" />

			<h5 className="mb-3">
				<i className="bi bi-download"></i> Data Export
			</h5>
			<p className="text-muted">Download all your job application data</p>
			<ActionButton
				variant="secondary"
				onClick={() => downloadJobsExport(token)}
				defaultIcon="download"
				defaultText="Download Data"
			/>

			<div className="mt-4">
				<ActionButton
					type="submit"
					variant="primary"
					disabled={submitting}
					defaultIcon="save"
					defaultText={submitting ? "Saving..." : "Save Account Settings"}
				/>
			</div>
		</Form>
	);
};
