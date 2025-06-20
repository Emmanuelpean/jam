import React, { useState } from "react";
import GenericTable, { createGenericDeleteHandler, createTableActions } from "../components/tables/GenericTable";
import KeywordFormModal from "../components/modals/keyword/KeywordFormModal";
import KeywordViewModal from "../components/modals/keyword/KeywordViewModal";
import { useTableData } from "../components/tables/Table";
import { useAuth } from "../contexts/AuthContext";
import useGenericAlert from "../hooks/useGenericAlert";
import AlertModal from "../components/modals/alert/AlertModal";
import { columns } from "../components/rendering/ColumnRenders";

const KeywordsPage = () => {
	const { token } = useAuth();
	const {
		data: keywords,
		setData: setKeywords,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("keywords");

	const [showModal, setShowModal] = useState(false);
	const [showViewModal, setShowViewModal] = useState(false);
	const [showEditModal, setShowEditModal] = useState(false);
	const [selectedKeyword, setSelectedKeyword] = useState(null);

	const { alertState, showConfirm, showError, hideAlert } = useGenericAlert();

	// Handle view keyword
	const handleView = (keyword) => {
		setSelectedKeyword(keyword);
		setShowViewModal(true);
	};

	// Handle edit keyword
	const handleEdit = (keyword) => {
		setSelectedKeyword(keyword);
		setShowEditModal(true);
	};

	// Handle edit success
	const handleEditSuccess = (updatedKeyword) => {
		updateItem(updatedKeyword);
		setShowEditModal(false);
		setSelectedKeyword(null);
	};

	// Handle edit modal close
	const handleEditModalClose = () => {
		setShowEditModal(false);
		setSelectedKeyword(null);
	};

	// Create reusable delete handler using the generic function
	const handleDelete = createGenericDeleteHandler({
		endpoint: "keywords",
		token,
		showConfirm,
		showError,
		removeItem,
		setData: setKeywords,
		nameKey: "name",
		itemType: "Keyword",
	});

	// Define table columns (without actions)
	const tableColumns = [columns.name, columns.createdAt];

	// Create standardised actions using the utility function
	const tableActions = createTableActions([
		{ type: "view", onClick: handleView },
		{ type: "edit", onClick: handleEdit },
		{ type: "delete", onClick: handleDelete },
	]);

	const handleAddSuccess = (newKeyword) => {
		addItem(newKeyword);
	};

	return (
		<div className="container">
			<h2 className="my-4">Tags</h2>

			<GenericTable
				data={keywords}
				columns={tableColumns}
				actions={tableActions}
				sortConfig={sortConfig}
				onSort={setSortConfig}
				searchTerm={searchTerm}
				onSearchChange={setSearchTerm}
				onAddClick={() => setShowModal(true)}
				addButtonText="Add Tag"
				loading={loading}
				error={error}
				emptyMessage="No tag found"
			/>

			{/* Modals */}
			<KeywordFormModal show={showModal} onHide={() => setShowModal(false)} onSuccess={handleAddSuccess} />

			<KeywordFormModal
				show={showEditModal}
				onHide={handleEditModalClose}
				onSuccess={handleEditSuccess}
				initialData={selectedKeyword || {}}
				isEdit={true}
			/>

			<KeywordViewModal
				show={showViewModal}
				onHide={() => setShowViewModal(false)}
				keyword={selectedKeyword}
				onEdit={handleEdit}
			/>

			{/* Alert Modal using GenericModal - handles both alerts and confirmations */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</div>
	);
};

export default KeywordsPage;
