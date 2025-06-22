import React from "react";
import GenericTable, { createGenericDeleteHandler, createTableActions } from "./GenericTable";
import AlertModal from "../modals/alert/AlertModal";
import useModalState from "../../hooks/useModalState";
import useGenericAlert from "../../hooks/useGenericAlert";
import { useAuth } from "../../contexts/AuthContext";

const GenericTableWithModals = ({
	// Table props
	data,
	columns,
	sortConfig,
	onSort,
	searchTerm,
	onSearchChange,
	addButtonText,
	loading,
	error,
	emptyMessage,
	onRowClick,
	selectable,

	// Modal configuration
	FormModal,
	ViewModal,

	// Data management
	endpoint,
	nameKey,
	itemType,
	addItem,
	updateItem,
	removeItem,
	setData,

	// Optional props for form modal
	formModalSize,
	viewModalSize,

	// Additional content (like maps)
	children,

	// Page title
	title,

	// NEW: Control container class
	isInModal = false,
	showAllEntries = false,
}) => {
	const { token } = useAuth();
	const { alertState, showConfirm, showError, hideAlert } = useGenericAlert();

	const {
		showModal,
		showViewModal,
		showEditModal,
		selectedItem,
		openAddModal,
		closeAddModal,
		openViewModal,
		closeViewModal,
		openEditModal,
		closeEditModal,
	} = useModalState();

	// Handle edit success
	const handleEditSuccess = (updatedItem) => {
		updateItem(updatedItem);
		closeEditModal();
	};

	// Handle add success
	const handleAddSuccess = (newItem) => {
		addItem(newItem);
		closeAddModal();
	};

	// Create reusable delete handler
	const handleDelete = createGenericDeleteHandler({
		endpoint,
		token,
		showConfirm,
		showError,
		removeItem,
		setData,
		nameKey,
		itemType,
	});

	// Wrap modal handlers to prevent event propagation when inside another modal
	const handleViewClick = (item, event) => {
		if (event) {
			event.preventDefault();
			event.stopPropagation();
		}
		openViewModal(item);
	};

	const handleEditClick = (item, event) => {
		if (event) {
			event.preventDefault();
			event.stopPropagation();
		}
		openEditModal(item);
	};

	const handleDeleteClick = (item, event) => {
		if (event) {
			event.preventDefault();
			event.stopPropagation();
		}
		handleDelete(item);
	};

	const handleAddClick = (event) => {
		if (event) {
			event.preventDefault();
			event.stopPropagation();
		}
		openAddModal();
	};

	// Create standardized actions with event handling
	const tableActions = createTableActions([
		{ type: "view", onClick: handleViewClick },
		{ type: "edit", onClick: handleEditClick },
		{ type: "delete", onClick: handleDeleteClick },
	]);

	// Choose container class based on context
	const containerClass = isInModal ? "table-container-modal" : "table-container";

	return (
		<div className={containerClass}>
			{title && <h2 className="my-4">{title}</h2>}

			<GenericTable
				data={data}
				columns={columns}
				actions={tableActions}
				sortConfig={sortConfig}
				onSort={onSort}
				searchTerm={searchTerm}
				onSearchChange={onSearchChange}
				onAddClick={handleAddClick}
				addButtonText={addButtonText}
				loading={loading}
				error={error}
				emptyMessage={emptyMessage}
				onRowClick={onRowClick}
				selectable={selectable}
				showAllEntries={showAllEntries}
			/>

			{/* Additional content (like maps) */}
			{children}

			{/* Modals */}
			{FormModal && (
				<>
					<FormModal
						show={showModal}
						onHide={closeAddModal}
						onSuccess={handleAddSuccess}
						size={formModalSize}
					/>

					<FormModal
						show={showEditModal}
						onHide={closeEditModal}
						onSuccess={handleEditSuccess}
						initialData={selectedItem || {}}
						isEdit={true}
						size={formModalSize}
					/>
				</>
			)}

			{ViewModal && (
				<ViewModal
					show={showViewModal}
					onHide={closeViewModal}
					{...{
						[nameKey === "title" ? "job" : nameKey === "name" ? itemType.toLowerCase() : "item"]:
							selectedItem,
					}}
					onEdit={handleEditClick}
					size={viewModalSize}
				/>
			)}

			{/* Alert Modal */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</div>
	);
};

export default GenericTableWithModals;
