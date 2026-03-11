import React, { useState } from "react";
import { Dropdown } from "react-bootstrap";
import DataTable from "../../components/DataTable/DataTable";
import { UserModal } from "../../components/DataModal/UserModal";
import { TableColumn, tableColumns } from "../../components/rendering/view/TableColumns";
import { GenericResponse, userApi } from "../../services/api/Users";
import { useAuth } from "../../contexts/AuthContext";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAlert } from "../../contexts/AlertContext";
import { useDataContext } from "../../contexts/DataContext";
import { ApiResponse } from "../../services/api/Base";
import { UserData } from "../../services/schemas/Core";
import { LAST_VERSION } from "../../releaseNotes/versions";

export const UserManagementPage: React.FC = () => {
	const { token } = useAuth();
	const { showToastSuccess, showToastError, showApiError } = useGlobalToast();
	const { showAlert } = useAlert();
	const { users } = useDataContext();
	const [sendingEmail, setSendingEmail] = useState<boolean>(false);

	const columns: TableColumn[] = [
		tableColumns.idColumn(),
		tableColumns.nameColumn(),
		tableColumns.emailColumn(),
		tableColumns.lastLoginColumn(),
		tableColumns.isAdminColumn(),
		tableColumns.isEnabledColumn(),
		tableColumns.toastActiveColumn(),
		tableColumns.createdAtColumn(),
	];

	const handleLogoutAllUsers = async (): Promise<void> => {
		const errorTitle = "Failed to log out all users";
		await showAlert({
			title: "Log Out All Users",
			message:
				"Are you sure you want to log out all users? This will invalidate all active sessions and force everyone to log in again.",
			type: "danger",
			confirmText: "Log Out Everyone",
			cancelText: "Cancel",
			icon: "bi bi-box-arrow-right",
			id: "logout-all-users-modal",
			onSuccess: async (): Promise<void> => {
				try {
					const response: ApiResponse<GenericResponse> = await userApi.invalidateAllSessions(token!);
					if (response.data.success) {
						showToastSuccess(response.data.message);
					} else {
						showToastError("Failed to invalidate sessions", errorTitle);
					}
				} catch (error) {
					showApiError(error, errorTitle, "An unknown error occurred during login.");
				}
			},
		});
	};

	const handleSendReleaseEmail = async (): Promise<void> => {
		const recipientCount: number = users.filter(
			(user: UserData): boolean => user.is_active && !user.is_demo && user.is_verified
		).length;
		const errorTitle = "Failed to send release email";

		await showAlert({
			title: `Send V${LAST_VERSION} Release Email`,
			message: `This will send the V${LAST_VERSION} release announcement email to ${recipientCount} active users. Do you want to proceed?`,
			type: "primary",
			confirmText: "Send Emails",
			cancelText: "Cancel",
			icon: "bi bi-envelope-fill",
			id: "send-release-email-modal",
			onSuccess: async (): Promise<void> => {
				try {
					setSendingEmail(true);
					const response: ApiResponse<GenericResponse> = await userApi.sendReleaseEmail(LAST_VERSION, token!);
					if (response.data.success) {
						showToastSuccess(response.data.message);
					} else {
						showToastError("Failed to send release emails", errorTitle);
					}
				} catch (error) {
					showApiError(error, errorTitle, "An unknown error occurred while sending release emails.");
				} finally {
					setSendingEmail(false);
				}
			},
		});
	};

	const toolbarAddon: JSX.Element = (
		<Dropdown style={{ height: "100%" }}>
			<Dropdown.Toggle
				style={{ height: "100%" }}
				variant="outline-primary"
				className="d-flex align-items-center"
				id="admin-actions-dropdown"
			>
				<i className="bi bi-gear me-2"></i>
				Actions
			</Dropdown.Toggle>
			<Dropdown.Menu>
				<Dropdown.Item onClick={handleSendReleaseEmail} disabled={sendingEmail}>
					<i className={`bi ${sendingEmail ? "bi-hourglass-split" : "bi-envelope"} me-2`}></i>
					{sendingEmail ? "Sending..." : `Send v${LAST_VERSION} Release Email`}
				</Dropdown.Item>
				<Dropdown.Divider />
				<Dropdown.Item onClick={handleLogoutAllUsers} className="text-danger">
					<i className="bi bi-box-arrow-right me-2"></i>
					Log Out All Users
				</Dropdown.Item>
			</Dropdown.Menu>
		</Dropdown>
	);

	return (
		<DataTable
			entityType="user"
			initialSortConfig={{ key: "id", direction: "asc" }}
			title="Users"
			columns={columns}
			Modal={UserModal}
			toolbarAddon={toolbarAddon}
		/>
	);
};
