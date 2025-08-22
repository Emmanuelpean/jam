import React, { useEffect } from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/TableSystem";
import { UserFormModal, UserViewModal } from "../components/modals/UserModal";
import { columns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext";

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

	const tableColumns = [
		columns.id(),
		columns.email(),
		columns.appTheme(),
		columns.last_login(),
		columns.isAdmin(),
		columns.createdAt(),
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
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
			FormModal={UserFormModal}
			ViewModal={UserViewModal}
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
