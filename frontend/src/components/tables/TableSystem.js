import React, { useEffect, useState } from "react";
import { Button, Form } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { api } from "../../services/api";
import { renderFieldValue } from "../rendering/Renders";
import { accessAttribute } from "../../utils/Utils";
import AlertModal from "../modals/alert/AlertModal";
import useModalState from "../../hooks/useModalState";
import useGenericAlert from "../../hooks/useGenericAlert";
import { pluralize } from "../../utils/StringUtils";

/**
 * Custom hook for managing table data with CRUD operations
 */
export const useTableData = (endpoint, dependencies = [], queryParams = {}) => {
	const { token } = useAuth();
	const navigate = useNavigate();
	const [data, setData] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);
	const [sortConfig, setSortConfig] = useState({ key: "created_at", direction: "desc" });
	const [searchTerm, setSearchTerm] = useState("");

	useEffect(() => {
		const fetchData = async () => {
			setLoading(true);
			try {
				const queryString =
					Object.keys(queryParams).length > 0 ? "?" + new URLSearchParams(queryParams).toString() : "";
				const result = await api.get(`${endpoint}/${queryString}`, token);
				setData(result);
			} catch (err) {
				console.error(`Error fetching ${endpoint}:`, err);
				setError(`Failed to load ${endpoint}. Please try again later.`);
			} finally {
				setLoading(false);
			}
		};

		fetchData().then(() => null);
	}, [token, navigate, endpoint, ...dependencies]);

	const addItem = (newItem) => setData((prev) => [newItem, ...prev]);
	const updateItem = (updatedItem) =>
		setData((prev) => prev.map((item) => (item.id === updatedItem.id ? updatedItem : item)));
	const deleteItem = (itemId) => setData((prev) => prev.filter((item) => item.id !== itemId));

	return {
		data,
		setData,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		deleteItem,
	};
};

/**
 * Creates a reusable delete handler for table items
 */
export const createGenericDeleteHandler = ({
	endpoint,
	token,
	showConfirm,
	showError,
	removeItem,
	setData,
	nameKey,
	itemType = "item",
}) => {
	return async (item) => {
		const itemName = item[nameKey];
		try {
			await showConfirm({
				title: `Delete ${itemType}`,
				message: `Are you sure you want to delete "${itemName}"? This action cannot be undone.`,
				confirmText: "Delete",
				cancelText: "Cancel",
			});

			await api.delete(`${endpoint}/${item.id}`, token);

			if (typeof removeItem === "function") {
				removeItem(item.id);
			} else if (typeof setData === "function") {
				setData((prevData) => prevData.filter((dataItem) => dataItem.id !== item.id));
			} else {
				window.location.reload();
			}
		} catch (error) {
			if (error.message !== "User cancelled") {
				console.error(`Error deleting ${itemType}:`, error);
				await showError({
					message: `Failed to delete ${itemType}. Please check your connection and try again.`,
				});
			}
		}
	};
};

/**
 * Comprehensive table component with modals, sorting, searching, and CRUD operations
 */
export const GenericTableWithModals = ({
	// Table data
	data = [],
	columns = [],
	loading = false,
	error = null,

	// Search and sort
	searchTerm = "",
	onSearchChange = () => {},
	sortConfig = { key: null, direction: "asc" },
	onSort = () => {},

	// Modal configuration
	FormModal,
	ViewModal,
	formModalSize,
	viewModalSize,

	// Data management
	endpoint,
	nameKey,
	itemType,
	addItem,
	updateItem,
	removeItem,
	setData,

	// Display options
	title,
	showAllEntries = false,
	isInModal = false,
	selectable = false,
	emptyMessage,

	// Additional content
	children,
}) => {
	const { token } = useAuth();
	const { alertState, showConfirm, showError, hideAlert } = useGenericAlert();
	const [contextMenu, setContextMenu] = useState(null);
	const [currentPage, setCurrentPage] = useState(0);
	const [pageSize, setPageSize] = useState(20);

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

	// Utility functions
	const getEffectiveItem = (item, column) => {
		if (!column || !column.accessKey) return item;
		return accessAttribute(item, column.accessKey);
	};

	const getColumnValue = (item, column, field) => {
		if (!column) return null;
		const effectiveItem = getEffectiveItem(item, column);
		if (column.accessor) return column.accessor(effectiveItem);
		if (field) return accessAttribute(effectiveItem, field);
		return accessAttribute(effectiveItem, column.key);
	};

	// Data processing
	const getSortedData = () => {
		let filteredData = [...data];

		// Filter by search term
		if (searchTerm && columns.some((col) => col.searchable)) {
			const searchTermLower = searchTerm.toLowerCase();
			filteredData = filteredData.filter((item) => {
				return columns.some((column) => {
					if (!column.searchable) return false;
					let value;
					if (column.searchFields) {
						if (typeof column.searchFields === "function") {
							const rawValue = getColumnValue(item, column);
							value = column.searchFields(rawValue);
						} else {
							const fields = Array.isArray(column.searchFields)
								? column.searchFields
								: [column.searchFields];
							value = fields
								.map((field) => getColumnValue(item, column, field))
								.filter((val) => val != null)
								.join(" ");
						}
					} else {
						value = getColumnValue(item, column);
					}
					return value?.toString().toLowerCase().includes(searchTermLower);
				});
			});
		}

		// Sort data
		if (sortConfig.key) {
			filteredData.sort((a, b) => {
				const column = columns.find((col) => col.key === sortConfig.key);
				let aValue, bValue;

				if (column?.sortFunction && typeof column.sortFunction === "function") {
					aValue = column.sortFunction(a);
					bValue = column.sortFunction(b);
				} else if (column?.sortField) {
					aValue = getColumnValue(a, column, column.sortField);
					bValue = getColumnValue(b, column, column.sortField);
				} else {
					aValue = getColumnValue(a, column);
					bValue = getColumnValue(b, column);
				}

				if (aValue == null && bValue == null) return 0;
				if (aValue == null) return 1;
				if (bValue == null) return -1;

				if (typeof aValue === "string" && typeof bValue === "string") {
					aValue = aValue.toLowerCase();
					bValue = bValue.toLowerCase();
				}

				if (aValue < bValue) return sortConfig.direction === "asc" ? -1 : 1;
				if (aValue > bValue) return sortConfig.direction === "asc" ? 1 : -1;
				return 0;
			});
		}

		return filteredData;
	};

	// Event handlers
	const handleSort = (key) => {
		let direction = "asc";
		if (sortConfig.key === key && sortConfig.direction === "asc") {
			direction = "desc";
		}
		onSort({ key, direction });
	};

	const handleRowClick = (event, item) => {
		if (contextMenu) return;

		const isInteractiveElement = (element) => {
			if (!element) return false;
			const tagName = element.tagName?.toLowerCase();
			return (
				["button", "a", "input", "select", "textarea"].includes(tagName) ||
				element.onclick ||
				element.getAttribute("onclick") ||
				element.classList?.contains("clickable-badge") ||
				element.classList?.contains("btn") ||
				element.style?.cursor === "pointer"
			);
		};

		let currentElement = event.target;
		while (currentElement && currentElement !== event.currentTarget) {
			if (isInteractiveElement(currentElement)) return;
			currentElement = currentElement.parentElement;
		}

		openViewModal(item);
	};

	const handleRowRightClick = (item, event) => {
		event.preventDefault();
		event.stopPropagation();
		setContextMenu({ item, x: event.clientX, y: event.clientY, show: true });
	};

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

	// Context menu handlers
	const handleContextAction = (action, e) => {
		e.stopPropagation();
		if (contextMenu?.item) {
			switch (action) {
				case "view":
					openViewModal(contextMenu.item);
					break;
				case "edit":
					openEditModal(contextMenu.item);
					break;
				case "delete":
					handleDelete(contextMenu.item);
					break;
			}
		}
		setContextMenu(null);
	};

	// Success handlers
	const handleEditSuccess = (updatedItem) => {
		updateItem(updatedItem);
		closeEditModal();
	};
	const handleAddSuccess = (newItem) => {
		addItem(newItem);
		closeAddModal();
	};

	// Close context menu on outside click or escape
	useEffect(() => {
		const handleGlobalClick = () => contextMenu && setContextMenu(null);
		const handleKeyPress = (e) => e.key === "Escape" && contextMenu && setContextMenu(null);

		if (contextMenu) {
			document.addEventListener("click", handleGlobalClick);
			document.addEventListener("keydown", handleKeyPress);
		}

		return () => {
			document.removeEventListener("click", handleGlobalClick);
			document.removeEventListener("keydown", handleKeyPress);
		};
	}, [contextMenu]);

	// Pagination
	const sortedData = getSortedData();
	const totalPages = Math.ceil(sortedData.length / pageSize);
	const startIndex = showAllEntries ? 0 : currentPage * pageSize;
	const endIndex = showAllEntries ? sortedData.length : startIndex + pageSize;
	const currentPageData = sortedData.slice(startIndex, endIndex);

	useEffect(() => setCurrentPage(0), [searchTerm, data]);

	const goToPage = (page) => setCurrentPage(Math.max(0, Math.min(totalPages - 1, page)));
	const handlePageSizeChange = (newPageSize) => {
		setPageSize(newPageSize);
		setCurrentPage(0);
	};

	// Render loading/error states
	if (loading) {
		return (
			<div className="d-flex justify-content-center mt-5">
				<div className="spinner-border" role="status" id="table-spinner">
					<span className="visually-hidden">Loading...</span>
				</div>
			</div>
		);
	}

	if (error) {
		return <div className="alert alert-danger mt-3">{error}</div>;
	}

	const containerClass = isInModal ? "table-container-modal" : "table-container";

	return (
		<div className={containerClass}>
			{title && <h2 className="my-4">{title}</h2>}

			{/* Header with search and add button */}
			<div className="d-flex justify-content-between mb-3" style={{ gap: "1rem" }}>
				<div className="d-flex align-items-center gap-3" style={{ width: "40%" }}>
					<input
						type="text"
						className="form-control"
						placeholder="Search..."
						value={searchTerm}
						onChange={(e) => onSearchChange(e.target.value)}
						id="search-input"
					/>
					<span className="text-muted small" style={{ whiteSpace: "nowrap" }}>
						Showing {sortedData.length} Entries
					</span>
				</div>
				<Button
					variant="primary"
					onClick={() => openAddModal()}
					style={{ width: "60%" }}
					id="add-entity-button"
				>
					Add {itemType}
				</Button>
			</div>

			{/* Table */}
			<div className="table-responsive">
				<table className="table table-striped table-hover rounded-3 overflow-hidden">
					<thead className="custom-header">
						<tr>
							{columns.map((column) => (
								<th key={column.key}>
									<div className="d-flex align-items-center justify-content-between">
										<div
											className={column.sortable ? "cursor-pointer user-select-none" : ""}
											onClick={() => column.sortable && handleSort(column.key)}
											id={`table-header-${column.key}`}
										>
											{column.label}
											{column.sortable && (
												<span className="ms-1">
													<i
														className={`bi bi-arrow-${
															sortConfig.key === column.key
																? sortConfig.direction === "asc"
																	? "up"
																	: "down"
																: "down-up"
														}`}
													></i>
												</span>
											)}
										</div>
									</div>
								</th>
							))}
						</tr>
					</thead>
					<tbody>
						{currentPageData.map((item, index) => (
							<tr
								key={item.id || index}
								id={`table-row-${item.id}`}
								className={`${selectable ? "table-row-selectable" : ""} table-row-clickable`}
								onClick={(e) => handleRowClick(e, item)}
								onContextMenu={(e) => handleRowRightClick(item, e)}
								style={{ cursor: "pointer" }}
							>
								{columns.map((column, columnIndex) => (
									<td
										key={column.key}
										className="align-middle"
										style={columnIndex === 0 ? { fontWeight: "bold" } : {}}
									>
										{renderFieldValue(column, item)}
									</td>
								))}
							</tr>
						))}
						{currentPageData.length === 0 && (
							<tr>
								<td colSpan={columns.length} className="text-center py-4 text-muted">
									{emptyMessage || `No ${pluralize(itemType)} found`}
								</td>
							</tr>
						)}
					</tbody>
				</table>
			</div>

			{/* Pagination */}
			{!showAllEntries && (
				<div className="d-flex justify-content-between align-items-center mt-3">
					<div className="d-flex align-items-center gap-1">
						{[
							{
								action: () => goToPage(0),
								disabled: currentPage === 0,
								icon: "chevron-double-left",
								label: "First",
							},
							{
								action: () => goToPage(currentPage - 1),
								disabled: currentPage === 0,
								icon: "chevron-left",
								label: "Previous",
							},
							{
								action: () => goToPage(currentPage + 1),
								disabled: currentPage >= totalPages - 1,
								icon: "chevron-right",
								label: "Next",
							},
							{
								action: () => goToPage(totalPages - 1),
								disabled: currentPage >= totalPages - 1,
								icon: "chevron-double-right",
								label: "Last",
							},
						].map(({ action, disabled, icon, label }) => (
							<Button
								key={label}
								variant="outline-secondary"
								size="sm"
								className="py-0 px-2"
								onClick={action}
								disabled={disabled}
								aria-label={label}
							>
								<i className={`bi bi-${icon}`} aria-hidden="true"></i>
							</Button>
						))}
					</div>
					<div className="d-flex align-items-center gap-2">
						<span className="small text-muted text-nowrap">
							Page {currentPage + 1} of {totalPages || 1}
						</span>
						<Form.Select
							size="sm"
							id="page-items-select"
							style={{ width: "auto", padding: "0.25rem 0.5rem", textAlign: "center" }}
							value={pageSize}
							onChange={(e) => handlePageSizeChange(Number(e.target.value))}
						>
							{[20, 30, 40, 50, 100].map((size) => (
								<option key={size} value={size}>
									Show {size} Entries
								</option>
							))}
						</Form.Select>
					</div>
				</div>
			)}

			{/* Context Menu */}
			{contextMenu?.show && (
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
					{[
						{ action: "view", icon: "eye", text: "View", id: "context-menu-view" },
						{ action: "edit", icon: "pencil", text: "Edit", id: "context-menu-edit" },
						{
							action: "delete",
							icon: "trash",
							text: "Delete",
							id: "context-menu-delete",
							color: "#dc3545",
						},
					].map(({ action, icon, text, id, color }) => (
						<div
							key={action}
							className="context-menu-item"
							style={{
								padding: "8px 16px",
								cursor: "pointer",
								fontSize: "14px",
								borderBottom: action !== "delete" ? "1px solid #eee" : "none",
								color: color || "inherit",
							}}
							onClick={(e) => handleContextAction(action, e)}
							onMouseEnter={(e) => (e.target.style.backgroundColor = "#f8f9fa")}
							onMouseLeave={(e) => (e.target.style.backgroundColor = "white")}
							id={id}
						>
							<i className={`bi bi-${icon} me-2`}></i>
							{text}
						</div>
					))}
				</div>
			)}

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
						data={selectedItem || {}}
						isEdit={true}
						size={formModalSize}
					/>
				</>
			)}

			{ViewModal && (
				<ViewModal
					show={showViewModal}
					onHide={closeViewModal}
					data={selectedItem}
					onEdit={() => {
						closeViewModal();
						openEditModal(selectedItem);
					}}
					size={viewModalSize}
				/>
			)}

			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</div>
	);
};

export default GenericTableWithModals;
