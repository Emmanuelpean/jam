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
import {pluralize} from "../../utils/StringUtils";

// ================================================================================================
// DATA MANAGEMENT HOOK
// ================================================================================================

/**
 * Custom hook for managing table data with CRUD operations
 * @param {string} endpoint - API endpoint for data fetching
 * @param {Array} dependencies - Additional dependencies for useEffect
 * @param {Object} queryParams - Query parameters for API requests
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
			if (!token) {
				navigate("/login");
				return;
			}

			setLoading(true);
			try {
				// Build query string from queryParams
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

		fetchData();
	}, [token, navigate, endpoint, ...dependencies]);

	const addItem = (newItem) => {
		setData((prev) => [newItem, ...prev]);
	};

	const updateItem = (updatedItem) => {
		setData((prev) => prev.map((item) => (item.id === updatedItem.id ? updatedItem : item)));
	};

	const deleteItem = (itemId) => {
		setData((prev) => prev.filter((item) => item.id !== itemId));
	};

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

// ================================================================================================
// DELETE HANDLER UTILITY
// ================================================================================================

/**
 * Creates a reusable delete handler for table items
 * @param {Object} params - Configuration object for delete handler
 */
export const createGenericDeleteHandler = ({
	endpoint, // String - API endpoint path (e.g., "users", "companies")
	token, // String - Authentication token for API requests
	showConfirm, // Function - Shows confirmation dialog before deletion
	showError, // Function - Shows error messages to user
	removeItem, // Function - Removes item from local state by ID
	setData, // Function - Updates the entire data array (fallback method)
	nameKey, // String - Object property to use as display name in confirmation dialog
	itemType = "item", // String - Human-readable type name for confirmation messages
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

			// If we reach here, user confirmed
			try {
				await api.delete(`${endpoint}/${item.id}`, token);

				// Try removeItem first, then setData, then reload as fallback
				if (typeof removeItem === "function") {
					removeItem(item.id);
				} else if (typeof setData === "function") {
					setData((prevData) => prevData.filter((dataItem) => dataItem.id !== item.id));
				} else {
					window.location.reload();
				}
			} catch (error) {
				console.error(`Error deleting ${itemType}:`, error);
				await showError({
					message: `Failed to delete ${itemType}. Please check your connection and try again.`,
				});
			}
		} catch (error) {}
	};
};

// ================================================================================================
// BASIC TABLE COMPONENT
// ================================================================================================

/**
 * Basic table component with sorting, searching, and pagination
 */
export const GenericTable = ({
	data = [], // Array - The dataset to display in the table
	columns = [], // Array - Column definitions with keys, labels, and render functions
	sortConfig = { key: null, direction: "asc" }, // Object - Current sort state (column key and direction)
	onSort = null, // Function - Called when user clicks sortable column headers
	searchTerm = "", // String - Current search/filter term
	onSearchChange = () => {}, // Function - Called when search input changes
	onAddClick = null, // Function - Called when "Add" button is clicked
	addButtonText = "Add", // String - Text to display on the add button
	loading = false, // Boolean - Shows loading spinner when true
	error = null, // String - Error message to display if data loading failed
	emptyMessage = "No data available", // String - Message shown when no data exists
	onRowClick = null, // Function - Called when a table row is clicked (receives item and event)
	onRowRightClick = null, // Function - Called when a table row is right-clicked (for context menus)
	selectable = false, // Boolean - Whether rows should have selection styling
	showAllEntries = false, // Boolean - If true, disables pagination and shows all data
}) => {
	const [currentPage, setCurrentPage] = useState(0);
	const [pageSize, setPageSize] = useState(20);

	const getEffectiveItem = (item, column) => {
		if (!column) {
			return item;
		}
		if (column.accessKey) {
			return accessAttribute(item, column.accessKey);
		}
		return item;
	};

	// Helper function to get value for searching/sorting
	const getColumnValue = (item, column, field) => {
		if (!column) {
			return null;
		}

		const effectiveItem = getEffectiveItem(item, column);

		if (column.accessor) {
			return column.accessor(effectiveItem);
		} else if (field) {
			return accessAttribute(effectiveItem, field);
		} else {
			return accessAttribute(effectiveItem, column.key);
		}
	};

	// Handle sorting
	const handleSort = (key) => {
		let direction = "asc";
		if (sortConfig.key === key && sortConfig.direction === "asc") {
			direction = "desc";
		}
		onSort({ key, direction });
	};

	// Handle row click with interactive element check
	const handleRowClick = (event, item) => {
		// Check if the clicked element or any parent is an interactive element
		const isInteractiveElement = (element) => {
			if (!element) return false;

			const tagName = element.tagName?.toLowerCase();
			const isButton = tagName === "button";
			const isLink = tagName === "a";
			const isInput = ["input", "select", "textarea"].includes(tagName);
			const hasOnClick = element.onclick || element.getAttribute("onclick");
			const isClickable =
				element.classList?.contains("clickable-badge") ||
				element.classList?.contains("btn") ||
				element.style?.cursor === "pointer";

			return isButton || isLink || isInput || hasOnClick || isClickable;
		};

		// Check the clicked element and its parents
		let currentElement = event.target;
		while (currentElement && currentElement !== event.currentTarget) {
			if (isInteractiveElement(currentElement)) {
				return; // Don't trigger row click if interactive element was clicked
			}
			currentElement = currentElement.parentElement;
		}

		// If we reach here, it's safe to trigger the row click
		if (onRowClick) {
			onRowClick(item);
		}
	};

	const getSortedData = () => {
		let filteredData = [...data];

		// Filter by search term if provided
		if (searchTerm && columns.some((col) => col.searchable)) {
			const searchTermLower = searchTerm.toLowerCase();
			filteredData = filteredData.filter((item) => {
				return columns.some((column) => {
					if (!column.searchable) return false;

					let value;
					if (column.searchFields) {
						// Handle multiple search fields
						const fields = Array.isArray(column.searchFields) ? column.searchFields : [column.searchFields];
						value = fields
							.map((field) => getColumnValue(item, column, field))
							.filter((val) => val != null)
							.join(" ");
					} else {
						// Use the column key with accessKey support
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

				// Enhanced sorting: Check sortFunction first, then sortField, then use getColumnValue
				if (column?.sortFunction && typeof column.sortFunction === "function") {
					// Use custom sorting function
					aValue = column.sortFunction(a);
					bValue = column.sortFunction(b);
				} else if (column?.sortField) {
					// Handle nested field sorting using getColumnValue
					aValue = getColumnValue(a, column, column.sortField);
					bValue = getColumnValue(b, column, column.sortField);
				} else {
					// Use getColumnValue with the column key and accessKey support
					aValue = getColumnValue(a, column);
					bValue = getColumnValue(b, column);
				}

				// Handle null/undefined values - always place them at the bottom
				if (aValue == null && bValue == null) return 0;
				if (aValue == null) return 1;
				if (bValue == null) return -1;

				// Convert to strings for comparison if needed
				if (typeof aValue === "string" && typeof bValue === "string") {
					aValue = aValue.toLowerCase();
					bValue = bValue.toLowerCase();
				}

				if (aValue < bValue) {
					return sortConfig.direction === "asc" ? -1 : 1;
				}
				if (aValue > bValue) {
					return sortConfig.direction === "asc" ? 1 : -1;
				}
				return 0;
			});
		}

		return filteredData;
	};

	// Create columns with actions if provided
	const tableColumns = [...columns];

	const sortedData = getSortedData();

	// Pagination logic
	const totalPages = Math.ceil(sortedData.length / pageSize);
	const startIndex = showAllEntries ? 0 : currentPage * pageSize;
	const endIndex = showAllEntries ? sortedData.length : startIndex + pageSize;
	const currentPageData = sortedData.slice(startIndex, endIndex);

	// Reset to first page when data changes
	React.useEffect(() => {
		setCurrentPage(0);
	}, [searchTerm, data]);

	// Pagination handlers
	const goToFirstPage = () => setCurrentPage(0);
	const goToPreviousPage = () => setCurrentPage(Math.max(0, currentPage - 1));
	const goToNextPage = () => setCurrentPage(Math.min(totalPages - 1, currentPage + 1));
	const goToLastPage = () => setCurrentPage(totalPages - 1);

	const handlePageSizeChange = (newPageSize) => {
		setPageSize(newPageSize);
		setCurrentPage(0);
	};

	if (loading) {
		return (
			<div className="d-flex justify-content-center mt-5">
				<div className="spinner-border" role="status">
					<span className="visually-hidden">Loading...</span>
				</div>
			</div>
		);
	}

	if (error) {
		return <div className="alert alert-danger mt-3">{error}</div>;
	}

	return (
		<div>
			{/* Header with search and add button */}
			<div className="d-flex justify-content-between mb-3" style={{ gap: "1rem" }}>
				<div className="d-flex align-items-center gap-3" style={{ width: "40%" }}>
					<input
						type="text"
						className="form-control"
						placeholder="Search..."
						value={searchTerm}
						onChange={(e) => onSearchChange(e.target.value)}
					/>
					<span className="text-muted small" style={{ whiteSpace: "nowrap" }}>
						Showing {sortedData.length} Entries
					</span>
				</div>

				<Button variant="primary" onClick={onAddClick} style={{ width: "60%" }}>
					{addButtonText}
				</Button>
			</div>

			{/* Table with rounded corners */}
			<div className="table-responsive">
				<table className="table table-striped table-hover rounded-3 overflow-hidden">
					<thead className="custom-header">
						<tr>
							{tableColumns.map((column) => (
								<th key={column.key}>
									<div className="d-flex align-items-center justify-content-between">
										<div
											className={column.sortable ? "cursor-pointer user-select-none" : ""}
											onClick={() => column.sortable && handleSort(column.key)}
										>
											{column.label}
											{column.sortable && (
												<span className="ms-1">
													{sortConfig.key === column.key &&
														sortConfig.direction === "asc" && (
															<i className="bi bi-arrow-up"></i>
														)}
													{sortConfig.key === column.key &&
														sortConfig.direction === "desc" && (
															<i className="bi bi-arrow-down"></i>
														)}
													{sortConfig.key !== column.key && (
														<i className="bi bi-arrow-down-up"></i>
													)}
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
								className={`${selectable ? "table-row-selectable" : ""} ${onRowClick ? "table-row-clickable" : ""}`}
								onClick={(e) => handleRowClick(e, item)}
								onContextMenu={onRowRightClick ? (e) => onRowRightClick(item, e) : undefined}
								style={{
									cursor: onRowClick || onRowRightClick ? "pointer" : "default",
								}}
							>
								{tableColumns.map((column, columnIndex) => (
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
								<td colSpan={tableColumns.length} className="text-center py-4 text-muted">
									{emptyMessage}
								</td>
							</tr>
						)}
					</tbody>
				</table>
			</div>

			{/* Page controls - Hidden when showAllEntries is true */}
			{!showAllEntries && (
				<div className="d-flex justify-content-between align-items-center mt-0ds">
					<div className="d-flex align-items-center gap-1">
						<Button
							variant="outline-secondary"
							size="sm"
							className="py-0 px-2"
							onClick={goToFirstPage}
							disabled={currentPage === 0}
							aria-label="First page"
						>
							<i className="bi bi-chevron-double-left" aria-hidden="true"></i>
						</Button>
						<Button
							variant="outline-secondary"
							size="sm"
							className="py-0 px-2"
							onClick={goToPreviousPage}
							disabled={currentPage === 0}
							aria-label="Previous page"
						>
							<i className="bi bi-chevron-left" aria-hidden="true"></i>
						</Button>
						<Button
							variant="outline-secondary"
							size="sm"
							className="py-0 px-2"
							onClick={goToNextPage}
							disabled={currentPage >= totalPages - 1}
							aria-label="Next page"
						>
							<i className="bi bi-chevron-right" aria-hidden="true"></i>
						</Button>
						<Button
							variant="outline-secondary"
							size="sm"
							className="py-0 px-2"
							onClick={goToLastPage}
							disabled={currentPage >= totalPages - 1}
							aria-label="Last page"
						>
							<i className="bi bi-chevron-double-right" aria-hidden="true"></i>
						</Button>
					</div>

					<div className="d-flex align-items-center gap-2">
						<span className="small text-muted">
							Page {currentPage + 1} of {totalPages || 1}
						</span>
						<Form.Select
							size="sm"
							style={{ width: "auto", padding: "0.25rem 0.5rem", textAlign: "center" }}
							value={pageSize}
							onChange={(e) => handlePageSizeChange(Number(e.target.value))}
						>
							{[10, 20, 30, 40, 50, 100].map((size) => (
								<option key={size} value={size}>
									Show {size} Entries
								</option>
							))}
						</Form.Select>
					</div>
				</div>
			)}
		</div>
	);
};

// ================================================================================================
// ENHANCED TABLE WITH MODALS
// ================================================================================================

/**
 * Enhanced table component with modal integration for CRUD operations
 */
export const GenericTableWithModals = ({
	// Table props
	data,
	columns,
	sortConfig,
	onSort,
	searchTerm,
	onSearchChange,
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

	// Control container class
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
				addButtonText={"Add " + itemType}
				loading={loading}
				error={error}
				emptyMessage={"No " + pluralize(itemType) + " found"}
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
						{...{
							[itemType.toLowerCase()]: selectedItem || {},
						}}
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

// ================================================================================================
// DEFAULT EXPORTS
// ================================================================================================

export default GenericTableWithModals;
