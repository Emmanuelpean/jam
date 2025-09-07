import React, { useEffect } from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/GenericTable.tsx";
import { UserModal } from "../components/modals/UserModal";
import { tableColumns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext.tsx";

export const UserManagementPage = () => {
	const { showLoading, hideLoading } = useLoading();
	const {
		data: users,
		setData: setUsers,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("users", [], {}, { key: "id", direction: "asc" });

	const columns = [
		tableColumns.id(),
		tableColumns.email(),
		tableColumns.appTheme(),
		tableColumns.last_login(),
		tableColumns.isAdmin(),
		tableColumns.createdAt(),
	];

	useEffect(() => {
		if (loading) {
			showLoading("Loading Users...");
		} else {
			hideLoading();
		}
		return () => {
			hideLoading();
		};
	}, [loading, showLoading, hideLoading]);

	return (
		<GenericTableWithModals
			title="Users"
			data={users}
			columns={columns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
			Modal={UserModal}
			endpoint="users"
			nameKey="email"
			itemType="User"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setUsers}
		/>
	);
};
