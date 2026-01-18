import React from "react";
import DataTable from "../components/tables/DataTable";
import { UserModal } from "../components/modals/UserModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

export const UserManagementPage: React.FC = () => {
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

	return (
		<DataTable
			entityType="user"
			initialSortConfig={{ key: "id", direction: "asc" }}
			title="Users"
			columns={columns}
			Modal={UserModal}
		/>
	);
};
