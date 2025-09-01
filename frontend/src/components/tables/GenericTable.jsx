import React, { useCallback, useEffect, useState } from "react";
import { Button, Form } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext.tsx";
import { api } from "../../services/Api.ts";
import { getTableIcon, renderFieldValue } from "../rendering/view/ViewRenders";
import { accessAttribute } from "../../utils/Utils.ts";
import AlertModal from "../modals/AlertModal";
import useModalState from "../../hooks/useModalState.ts";
import useGenericAlert from "../../hooks/useGenericAlert.ts";
import { pluralize } from "../../utils/StringUtils.ts";

/**
 * Custom hook for managing table data with CRUD operations
 */
export const useTableData = (
	endpoint,
	dependencies = [],
	queryParams = {},
	customSortConfig = {},
	providedData = null,
) => {
	const { token } = useAuth();

	const [data, setData] = useState(providedData || []);
	const [loading, setLoading] = useState(!providedData);
	const [error, setError] = useState(null);
	const [sortConfig, setSortConfig] = useState(customSortConfig || { key: "created_at", direction: "desc" });
	const [searchTerm, setSearchTerm] = useState("");

	// Memoize the fetch function to prevent unnecessary re-renders
	// noinspection com.intellij.reactbuddy.ExhaustiveDepsInspection
	const fetchData = useCallback(async () => {
		setLoading(true);
		try {
			const queryString =
				Object.keys(queryParams).length > 0 ? "?" + new URLSearchParams(queryParams).toString() : "";
			const result = await api.get(`${endpoint}/${queryString}`, token);
			setData(result || []); // Ensure result is always an array
		} catch (err) {
			console.error(`Error fetching ${endpoint}:`, err);
			setError(`Failed to load ${endpoint}. Please try again later.`);
		} finally {
			setLoading(false);
		}
	}, [endpoint, token, JSON.stringify(queryParams)]);

	useEffect(() => {
		// If data is provided, use it directly
		if (providedData !== null) {
			setData(providedData);
			setLoading(false);
		} else if (token) {
			fetchData().then(() => null);
		}
	}, [token, fetchData, providedData, ...dependencies]);

	const addItem = useCallback((newItem) => setData((prev) => [newItem, ...prev]), []);
	const updateItem = useCallback(
		(updatedItem) => setData((prev) => prev.map((item) => (item.id === updatedItem.id ? updatedItem : item))),
		[],
	);
	const deleteItem = useCallback((itemId) => setData((prev) => prev.filter((item) => item.id !== itemId)), []);

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
		refetch: fetchData,
	};
};

/**
 * Creates a reusable delete handler for table items
 */
export const createGenericDeleteHandler = ({
	endpoint,
	token,
	showDelete,
	showError,
	removeItem,
	setData,
	nameKey,
	itemType = "item",
}) => {
	return async (item) => {
		const itemName = item[nameKey];
		try {
			await showDelete({
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
			if (error !== false) {
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
	sortConfig = { key: "", direction: "asc" },
	onSort = () => {},

	// Modal configuration
	FormModal,
	ViewModal,
	ModalSize = "lg",

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
	selectable = false,
	emptyMessage,
	compact = false,
	showSearch = true,
	showAdd = true,

	// Additional content
	children,
}) => {
	const { token } = useAuth();
	const { alertState, showDelete, showError, hideAlert } = useGenericAlert();
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
		endpoint: endpoint,
		token: token,
		showDelete: showDelete,
		showError: showError,
		removeItem: removeItem,
		setData: setData,
		nameKey: nameKey,
		itemType: itemType,
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
				default:
					handleDelete(contextMenu.item).then(() => null);
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

	// noinspection JSValidateTypes
	return (
		<div className={"table-container"}>
			{title && (
				<div className="table-header-section mb-4">
					<div className="d-flex align-items-center justify-content-between p-4 border-0 bg-white shadow-sm rounded-3">
						<div className="d-flex align-items-center">
							<div className="header-icon-wrapper me-3">
								<i className={getTableIcon(title)}></i>
							</div>
							<h4 className="mb-0 fw-bold text-dark">{title}</h4>
						</div>
						{data.length > 0 && <div className="table-count-badge">{data.length}</div>}
					</div>
				</div>
			)}

			<div
				className={`d-flex justify-content-between ${compact ? "mb-2" : "mb-3"}`}
				style={{ gap: compact ? "0.5rem" : "1rem" }}
			>
				{showSearch && !compact && (
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
				)}
				{showAdd && (
					<Button
						variant="primary"
						size={compact ? "sm" : undefined}
						onClick={() => openAddModal()}
						className="d-flex align-items-center justify-content-center"
						style={{
							width: compact ? "100%" : "60%",
							fontSize: compact ? "0.875rem" : undefined,
							padding: compact ? "0.25rem 0.5rem" : undefined,
							height: compact ? "2rem" : undefined,
						}}
						id="add-entity-button"
					>
						<i className="bi bi-plus-circle me-2" style={{ fontSize: "1.1rem" }}></i>
						Add {itemType}
					</Button>
				)}
			</div>

			{/* Table */}
			<div className="table-responsive">
				<table
					className={`table table-striped table-hover rounded-3 overflow-hidden ${compact ? "table-sm" : ""}`}
					style={compact ? { fontSize: "0.875rem" } : {}}
				>
					<thead className="custom-header">
						<tr>
							{columns.map((column) => (
								<th key={column.key} style={compact ? { padding: "0.5rem" } : {}}>
									<div className="d-flex align-items-center justify-content-between">
										<div
											className={column.sortable ? "cursor-pointer user-select-none" : ""}
											onClick={() => column.sortable && handleSort(column.key)}
											id={`table-header-${column.key}`}
											style={compact ? { fontSize: "0.875rem" } : {}}
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
														style={compact ? { fontSize: "0.75rem" } : {}}
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
										style={{
											...(columnIndex === 0 ? { fontWeight: "bold" } : {}),
											...(compact
												? {
														padding: "0.5rem",
														fontSize: "0.875rem",
													}
												: {}),
										}}
									>
										{renderFieldValue(column, item, `table-row-${item.id}`)}
									</td>
								))}
							</tr>
						))}
						{currentPageData.length === 0 && (
							<tr>
								<td
									colSpan={columns.length}
									className="text-center py-4 text-muted"
									style={
										compact
											? {
													padding: "1rem",
													fontSize: "0.875rem",
												}
											: {}
									}
								>
									{emptyMessage || `No ${pluralize(itemType)} found`}
								</td>
							</tr>
						)}
					</tbody>
				</table>
			</div>

			{/* Pagination */}
			{!showAllEntries && (
				<div className={`d-flex justify-content-between align-items-center mt-0`}>
					<div className="d-flex align-items-center gap-0">
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
								className={compact ? "py-0 px-1" : "py-0 px-2"}
								onClick={action}
								disabled={disabled}
								aria-label={label}
								style={compact ? { fontSize: "0.75rem" } : {}}
							>
								<i className={`bi bi-${icon}`} aria-hidden="true"></i>
							</Button>
						))}
					</div>
					<div className="d-flex align-items-center gap-2">
						<span className={`small text-muted text-nowrap`} style={compact ? { fontSize: "0.75rem" } : {}}>
							Page {currentPage + 1} of {totalPages || 1}
						</span>
						<Form.Select
							size="sm"
							id="page-items-select"
							style={{
								width: "auto",
								padding: compact ? "0.125rem 0.25rem" : "0.25rem 0.5rem",
								textAlign: "center",
								fontSize: compact ? "0.75rem" : undefined,
							}}
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
						minWidth: compact ? "120px" : "150px",
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
								padding: compact ? "6px 12px" : "8px 16px",
								cursor: "pointer",
								fontSize: compact ? "13px" : "14px",
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
			<FormModal
				show={showModal}
				onHide={closeAddModal}
				onSuccess={handleAddSuccess}
				size={ModalSize}
				data={{}}
				isEdit={false}
			/>

			<FormModal
				show={showEditModal}
				onHide={closeEditModal}
				onSuccess={handleEditSuccess}
				data={selectedItem || {}}
				isEdit={true}
				size={ModalSize}
			/>

			<ViewModal
				show={showViewModal}
				onHide={closeViewModal}
				onSuccess={handleAddSuccess}
				data={selectedItem}
				onEdit={() => {
					closeViewModal();
					openEditModal(selectedItem);
				}}
				size={ModalSize}
			/>

			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</div>
	);
};

export default GenericTableWithModals;
