import React, { useEffect, useState } from "react";
import GenericTable, { createGenericDeleteHandler } from "./GenericTable";
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
	const [contextMenu, setContextMenu] = useState(null);

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

	// Close context menu when clicking anywhere or pressing Escape
	useEffect(() => {
		const handleGlobalClick = () => {
			if (contextMenu) {
				setContextMenu(null);
			}
		};

		const handleKeyPress = (e) => {
			if (e.key === "Escape" && contextMenu) {
				setContextMenu(null);
			}
		};

		if (contextMenu) {
			document.addEventListener("click", handleGlobalClick);
			document.addEventListener("keydown", handleKeyPress);
		}

		return () => {
			document.removeEventListener("click", handleGlobalClick);
			document.removeEventListener("keydown", handleKeyPress);
		};
	}, [contextMenu]);

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

	// Handle row click to open view modal (only if no context menu is open)
	const handleRowClick = (item, event) => {
		if (contextMenu) {
			// If context menu is open, don't trigger row click
			return;
		}

		if (event) {
			event.preventDefault();
			event.stopPropagation();
		}
		openViewModal(item);
	};

	// Handle right-click context menu
	const handleRowRightClick = (item, event) => {
		event.preventDefault();
		event.stopPropagation();

		setContextMenu({
			item,
			x: event.clientX,
			y: event.clientY,
			show: true,
		});
	};

	// Context menu actions
	const handleContextView = (e) => {
		e.stopPropagation();
		if (contextMenu?.item) {
			openViewModal(contextMenu.item);
		}
		setContextMenu(null);
	};

	const handleContextEdit = (e) => {
		e.stopPropagation();
		if (contextMenu?.item) {
			openEditModal(contextMenu.item);
		}
		setContextMenu(null);
	};

	const handleContextDelete = (e) => {
		e.stopPropagation();
		if (contextMenu?.item) {
			handleDelete(contextMenu.item);
		}
		setContextMenu(null);
	};

	const handleAddClick = (event) => {
		if (event) {
			event.preventDefault();
			event.stopPropagation();
		}
		openAddModal();
	};

	// Choose container class based on context
	const containerClass = isInModal ? "table-container-modal" : "table-container";

	return (
		<div className={containerClass}>
			{title && <h2 className="my-4">{title}</h2>}

			<GenericTable
				data={data}
				columns={columns}
				actions={null} // Completely remove actions
				sortConfig={sortConfig}
				onSort={onSort}
				searchTerm={searchTerm}
				onSearchChange={onSearchChange}
				onAddClick={handleAddClick}
				addButtonText={addButtonText}
				loading={loading}
				error={error}
				emptyMessage={emptyMessage}
				onRowClick={handleRowClick}
				onRowRightClick={handleRowRightClick}
				selectable={selectable}
				showAllEntries={showAllEntries}
			/>

			{/* Context Menu */}
			{contextMenu && contextMenu.show && (
				<div
					className="context-menu"
					style={{
						position: "fixed",
						top: contextMenu.y,
						left: contextMenu.x,
						zIndex: 9999,
						backgroundColor: "white",
						border: "1px solid #ccc",
						borderRadius: "4px",
						boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
						padding: "4px 0",
						minWidth: "150px",
					}}
					onClick={(e) => e.stopPropagation()}
				>
					<div
						className="context-menu-item"
						style={{
							padding: "8px 16px",
							cursor: "pointer",
							fontSize: "14px",
							borderBottom: "1px solid #eee",
						}}
						onClick={handleContextView}
						onMouseEnter={(e) => (e.target.style.backgroundColor = "#f8f9fa")}
						onMouseLeave={(e) => (e.target.style.backgroundColor = "white")}
					>
						<i className="bi bi-eye me-2"></i>View
					</div>
					<div
						className="context-menu-item"
						style={{
							padding: "8px 16px",
							cursor: "pointer",
							fontSize: "14px",
							borderBottom: "1px solid #eee",
						}}
						onClick={handleContextEdit}
						onMouseEnter={(e) => (e.target.style.backgroundColor = "#f8f9fa")}
						onMouseLeave={(e) => (e.target.style.backgroundColor = "white")}
					>
						<i className="bi bi-pencil me-2"></i>Edit
					</div>
					<div
						className="context-menu-item"
						style={{
							padding: "8px 16px",
							cursor: "pointer",
							fontSize: "14px",
							color: "#dc3545",
						}}
						onClick={handleContextDelete}
						onMouseEnter={(e) => (e.target.style.backgroundColor = "#f8f9fa")}
						onMouseLeave={(e) => (e.target.style.backgroundColor = "white")}
					>
						<i className="bi bi-trash me-2"></i>Delete
					</div>
				</div>
			)}

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
					onEdit={() => {
						closeViewModal();
						openEditModal(selectedItem);
					}}
					size={viewModalSize}
				/>
			)}

			{/* Alert Modal */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</div>
	);
};

export default GenericTableWithModals;
