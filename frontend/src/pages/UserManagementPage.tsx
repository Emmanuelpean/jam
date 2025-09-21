import React from "react";
import GenericTable from "../components/tables/GenericTable";
import { UserModal } from "../components/modals/UserModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

export const UserManagementPage: React.FC = () => {
	const columns = [
		tableColumns.id(),
		tableColumns.email(),
		tableColumns.appTheme(),
		tableColumns.last_login(),
		tableColumns.isAdmin(),
		tableColumns.createdAt(),
	];

	return (
		<GenericTable
			mode="api"
			endpoint="users"
			initialSortConfig={{ key: "id", direction: "asc" }}
			title="Users"
			columns={columns}
			Modal={UserModal}
			nameKey="email"
			itemType="User"
		/>
	);
};
