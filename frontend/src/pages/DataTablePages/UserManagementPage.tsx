import React from "react";
import { Button } from "react-bootstrap";
import DataTable from "../../components/DataTable/DataTable";
import { UserModal } from "../../components/DataModal/UserModal";
import { tableColumns } from "../../components/rendering/view/TableColumns";
import { GenericResponse, userApi } from "../../services/api/Users";
import { useAuth } from "../../contexts/AuthContext";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAlert } from "../../contexts/AlertContext";
import { ApiResponse } from "../../services/api/Base";

export const UserManagementPage: React.FC = () => {
	const { token } = useAuth();
	const { showToastSuccess, showToastError, showApiError } = useGlobalToast();
	const { showAlert } = useAlert();

	const columns = [
		tableColumns.idColumn(),
		tableColumns.nameColumn(),
		tableColumns.emailColumn(),
		tableColumns.lastLoginColumn(),
		tableColumns.isAdminColumn(),
		tableColumns.isActiveColumn(),
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

	const toolbarAddon: JSX.Element = (
		<Button
			variant={"outline-danger"}
			onClick={handleLogoutAllUsers}
			className="d-flex align-items-center"
			id="logout-all-users-button"
			style={{ height: "100%" }}
		>
			<i className="bi bi-box-arrow-right me-2"></i>
			Log Out All Users
		</Button>
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
