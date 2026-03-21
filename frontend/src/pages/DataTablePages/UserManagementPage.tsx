import React, { JSX, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Dropdown } from "react-bootstrap";
import DataTable from "../../components/DataTable/DataTable";
import { UserModal } from "../../components/DataModal/UserModal";
import { SettingModal } from "../../components/DataModal/SettingModal";
import { TableColumn, tableColumns } from "../../components/rendering/view/TableColumns";
import { GenericResponse, userApi } from "../../services/api/Users";
import { useAuth } from "../../contexts/AuthContext";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAlert } from "../../contexts/AlertContext";
import { useDataContext } from "../../contexts/DataContext";
import { ApiResponse } from "../../services/api/Base";
import { UserData } from "../../services/schemas/Core";
import { LAST_VERSION } from "../../releaseNotes/versions";
import { getTableIcon } from "../../components/rendering/view/Icons";
import PageHeader from "../PageHeader/PageHeader";
import { EmailTemplatesContent } from "../Admin/EmailTemplatesPage";

type ActiveTab = "users" | "settings" | "email-templates";

export const UserManagementPage: React.FC = () => {
	const { token } = useAuth();
	const { showToastSuccess, showToastError, showApiError } = useGlobalToast();
	const { showAlert } = useAlert();
	const { users } = useDataContext();
	const location = useLocation();
	const navigate = useNavigate();
	const [sendingEmail, setSendingEmail] = useState<boolean>(false);
	const activeTab: ActiveTab =
		location.pathname === "/app/settings"
			? "settings"
			: location.pathname === "/app/email-templates"
				? "email-templates"
				: "users";
	const [usersCount, setUsersCount] = useState<number>(0);
	const [settingsCount, setSettingsCount] = useState<number>(0);
	const [usersReload, setUsersReload] = useState<number>(0);
	const [settingsReload, setSettingsReload] = useState<number>(0);

	const userColumns: TableColumn[] = [
		tableColumns.idColumn(),
		tableColumns.nameColumn(),
		tableColumns.emailColumn(),
		tableColumns.lastLoginColumn(),
		tableColumns.isAdminColumn(),
		tableColumns.isEnabledColumn(),
		tableColumns.toastActiveColumn(),
		tableColumns.createdAtColumn(),
	];

	const settingColumns: TableColumn[] = [
		tableColumns.nameColumn(),
		tableColumns.valueColumn(),
		tableColumns.descriptionColumn(),
		tableColumns.isEnabledColumn(),
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
		<div>
			<div className="d-flex gap-3">
				<PageHeader
					className="flex-fill"
					title="Users"
					icon={getTableIcon("Users")}
					count={usersCount}
					onClick={(): void => {
						navigate("/app/users");
						setUsersReload((n) => n + 1);
					}}
					active={activeTab === "users"}
				/>
				<PageHeader
					className="flex-fill"
					title="Settings"
					icon={getTableIcon("Settings")}
					count={settingsCount}
					onClick={(): void => {
						navigate("/app/settings");
						setSettingsReload((n) => n + 1);
					}}
					active={activeTab === "settings"}
				/>
				<PageHeader
					className="flex-fill"
					title="Email Templates"
					icon={getTableIcon("Email Templates")}
					onClick={(): void => {
						navigate("/app/email-templates");
					}}
					active={activeTab === "email-templates"}
				/>
			</div>

			<div style={{ display: activeTab === "users" ? "block" : "none" }}>
				<DataTable
					entityType="user"
					initialSortConfig={{ key: "id", direction: "asc" }}
					columns={userColumns}
					Modal={UserModal}
					toolbarAddon={toolbarAddon}
					onTotalCountChange={setUsersCount}
					reloadTrigger={usersReload}
				/>
			</div>
			<div style={{ display: activeTab === "settings" ? "block" : "none" }}>
				<DataTable
					entityType="setting"
					initialSortConfig={{ key: "name", direction: "asc" }}
					columns={settingColumns}
					Modal={SettingModal}
					initialData={{ is_active: true }}
					onTotalCountChange={setSettingsCount}
					reloadTrigger={settingsReload}
				/>
			</div>
			{activeTab === "email-templates" && <EmailTemplatesContent />}
		</div>
	);
};
