import React, { useState } from "react";
import GenericTable, { createGenericDeleteHandler, createTableActions } from "../components/tables/GenericTable";
import CompanyFormModal from "../components/modals/CompanyFormModal";
import CompanyViewModal from "../components/modals/CompanyViewModal";
import { useTableData } from "../components/tables/Table";
import { useAuth } from "../contexts/AuthContext";
import useGenericAlert from "../hooks/useGenericAlert";
import AlertModal from "../components/AlertModal";
import { columns } from "../components/tables/ColumnDefinitions";

const CompaniesPage = () => {
	const { token } = useAuth();
	const {
		data: companies,
		setData: setCompanies,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("companies");

	const [showModal, setShowModal] = useState(false);
	const [showViewModal, setShowViewModal] = useState(false);
	const [showEditModal, setShowEditModal] = useState(false);
	const [selected, setSelected] = useState(null);

	const { alertState, showConfirm, showError, hideAlert } = useGenericAlert();

	// Handle view company
	const handleView = (company) => {
		setSelected(company);
		setShowViewModal(true);
	};

	// Handle edit company
	const handleEdit = (company) => {
		setSelected(company);
		setShowEditModal(true);
	};

	// Handle edit success
	const handleEditSuccess = (updatedCompany) => {
		updateItem(updatedCompany);
		setShowEditModal(false);
		setSelected(null);
	};

	// Handle edit modal close
	const handleEditModalClose = () => {
		setShowEditModal(false);
		setSelected(null);
	};

	// Create reusable delete handler using the generic function
	const handleDelete = createGenericDeleteHandler({
		endpoint: "companies",
		token,
		showConfirm,
		showError,
		removeItem,
		setData: setCompanies,
		nameKey: "name",
		itemType: "Company",
	});

	// Define table columns (without actions)
	const tableColumns = [columns.name, columns.description, columns.url, columns.createdAt];

	// Create standardized actions using the utility function
	const tableActions = createTableActions([
		{ type: "view", onClick: handleView },
		{ type: "edit", onClick: handleEdit },
		{ type: "delete", onClick: handleDelete },
	]);

	const handleAddSuccess = (newCompany) => {
		addItem(newCompany);
	};

	return (
		<div className="container">
			<h2 className="my-4">Companies</h2>

			<GenericTable
				data={companies}
				columns={tableColumns}
				actions={tableActions}
				sortConfig={sortConfig}
				onSort={setSortConfig}
				searchTerm={searchTerm}
				onSearchChange={setSearchTerm}
				onAddClick={() => setShowModal(true)}
				addButtonText="Add Company"
				loading={loading}
				error={error}
				emptyMessage="No companies found"
				onRowClick={handleView}
				selectable={true}
			/>

			{/* Modals */}
			<CompanyFormModal show={showModal} onHide={() => setShowModal(false)} onSuccess={handleAddSuccess} />

			<CompanyFormModal
				show={showEditModal}
				onHide={handleEditModalClose}
				onSuccess={handleEditSuccess}
				initialData={selected || {}}
				isEdit={true}
			/>

			<CompanyViewModal
				show={showViewModal}
				onHide={() => setShowViewModal(false)}
				company={selected}
				onEdit={handleEdit}
			/>

			{/* Alert Modal using GenericModal - handles both alerts and confirmations */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</div>
	);
};

export default CompaniesPage;
