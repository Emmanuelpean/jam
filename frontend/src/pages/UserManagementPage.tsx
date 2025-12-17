import React from "react";
import DataTable from "../components/tables/DataTable";
import { UserModal } from "../components/modals/UserModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

export const UserManagementPage: React.FC = () => {
	const columns = [
		tableColumns.idColumn(),
		tableColumns.emailColumn(),
		tableColumns.appThemeColumn(),
		tableColumns.lastLoginColumn(),
		tableColumns.isAdminColumn(),
		tableColumns.isActiveColumn(),
		tableColumns.toastActiveColumn(),
		tableColumns.createdAtColumn(),
	];

	return (
		<DataTable
			entityType="users"
			initialSortConfig={{ key: "id", direction: "asc" }}
			title="Users"
			columns={columns}
			Modal={UserModal}
			nameKey="email"
			itemType="User"
		/>
	);
};
