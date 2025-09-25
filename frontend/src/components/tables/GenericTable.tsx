import React, { MouseEvent, ReactNode, useCallback, useEffect, useState } from "react";
import { Button, Form } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { api } from "../../services/Api";
import { getTableIcon, renderViewField } from "../rendering/view/ViewRenders";
import { accessAttribute, normaliseList } from "../../utils/Utils";
import AlertModal from "../modals/AlertModal";
import useModalState from "../../hooks/useModalState";
import useGenericAlert from "../../hooks/useGenericAlert";
import { pluralize } from "../../utils/StringUtils";
import { TableColumn } from "../rendering/view/TableColumns";
import "./GenericTable.css";
import { useLoading } from "../../contexts/LoadingContext";

export interface CreateGenericDeleteHandlerProps {
	endpoint: string;
	token: string | null;
	showDelete: (config: any) => Promise<boolean>;
	showError: (config: any) => Promise<boolean>;
	removeItem: (itemId: string | number) => void;
	setData?: React.Dispatch<React.SetStateAction<any[]>>;
	nameKey: string;
	itemType?: string;
}

/**
 * Creates a reusable delete handler for table items
 */
export const createGenericDeleteHandler = ({
	// TODO merge with modal delete handler?
	endpoint,
	token,
	showDelete,
	showError,
	removeItem,
	nameKey,
	itemType = "item",
}: CreateGenericDeleteHandlerProps) => {
	return async (item: any): Promise<void> => {
		let message: string;
		if (nameKey !== "date") {
			message = `Are you sure you want to delete "${item[nameKey]}"? This action cannot be undone.`;
		} else {
			message = `Are you sure you want to delete this ${itemType}? This action cannot be undone.`;
		}
		try {
			await showDelete({
				title: `Delete ${itemType}`,
				message: message,
				confirmText: "Delete",
				cancelText: "Cancel",
			});

			await api.delete(`${endpoint}/${item.id}`, token);
			removeItem(item.id);
		} catch (error) {
			if (error !== false) {
				await showError({
					message: `Failed to delete ${itemType}. Please check your connection and try again.`,
				});
			}
		}
	};
};

export type Direction = "asc" | "desc";

export interface SortConfig {
	key: string;
	direction: Direction;
}

export interface ContextMenuState {
	item: any;
	x: number;
	y: number;
	show: boolean;
}

export interface DataTableProps {
	data?: any | null;
	columns?: TableColumn[];
	onDataChange?: (data: any[]) => void;
	error?: string | null;
	showAdd?: boolean;
}

export interface GenericTableProps {
	// Data source configuration
	mode: "api" | "controlled";

	// For API mode
	endpoint?: string;

	// For controlled mode
	data?: any[];
	onDataChange?: (data: any[]) => void;
	error?: string | null;

	// Table configuration
	columns?: TableColumn[];
	initialSortConfig?: Partial<SortConfig>;

	// Modal configuration
	Modal: React.ComponentType<any>;
	modalSize?: string;
	modalProps?: any;

	// Data management
	nameKey: string;
	itemType: string;

	// Display options
	title?: string;
	showAllEntries?: boolean;
	emptyMessage?: string;
	compact?: boolean;
	showSearch?: boolean;
	showAdd?: boolean;

	// Additional content
	children?: (data: any[]) => ReactNode;
}

export const GenericTable: React.FC<GenericTableProps> = ({
	// Data source configuration
	mode,
	endpoint = "",
	data: controlledData = [],
	onDataChange,

	// Table configuration
	columns = [],
	initialSortConfig = {},

	// Modal configuration
	Modal,
	modalSize = "lg",
	modalProps = {},

	// Data management
	nameKey,
	itemType,

	// Display options
	title,
	showAllEntries = false,
	emptyMessage,
	compact = false,
	showSearch = true,
	showAdd = true,

	// Additional content
	children,
}) => {
	const { token } = useAuth();
	const { alertState, showDelete, showError, hideAlert } = useGenericAlert();

	// Internal state management
	const [internalData, setInternalData] = useState<any[]>([]);
	const [error, setError] = useState<string | null>(null);

	// Search and sort
	const [sortConfig, setSortConfig] = useState<SortConfig>(
		(initialSortConfig as SortConfig) || { key: "created_at", direction: "desc" },
	);
	const [searchTerm, setSearchTerm] = useState<string>("");

	// UI state
	const [contextMenu, setContextMenu] = useState<ContextMenuState | null>(null);
	const [currentPage, setCurrentPage] = useState<number>(0);
	const [pageSize, setPageSize] = useState<number>(20);
	const { showLoading, hideLoading } = useLoading();

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

	const fetchData = useCallback(async (): Promise<void> => {
		// Fetch the data through the API
		if (mode !== "api" || !endpoint) {
			return;
		}
		showLoading();
		setError(null);
		try {
			const result = await api.get(`${endpoint}`, token);
			setInternalData(result);
		} catch (err) {
			setError(`Failed to load ${endpoint}. Please try again later.`);
			setInternalData([]);
		} finally {
			hideLoading();
		}
	}, [endpoint, token, mode]);

	useEffect(() => {
		// Handle data updates based on mode
		switch (mode) {
			case "api":
				if (token) {
					fetchData().then(() => {});
				}
				break;
			case "controlled":
				break;
		}
	}, [mode, token, fetchData]);

	const getEffectiveData = (): any[] => {
		// Get effective data based on mode
		switch (mode) {
			case "controlled":
				return controlledData;
			case "api":
				return internalData;
		}
	};

	// CRUD operations
	const addItem = useCallback(
		(newItem: any) => {
			if (mode === "controlled") {
				const newData = [newItem, ...controlledData];
				onDataChange?.(newData);
			} else {
				setInternalData((prev) => [newItem, ...prev]);
			}
		},
		[mode, controlledData, onDataChange],
	);

	const updateItem = useCallback(
		(updatedItem: any) => {
			if (updatedItem) {
				if (mode === "controlled") {
					const newData = controlledData.map((item) => (item.id === updatedItem.id ? updatedItem : item));
					onDataChange?.(newData);
				} else {
					setInternalData((prev) => prev.map((item) => (item.id === updatedItem.id ? updatedItem : item)));
				}
			}
		},
		[mode, controlledData, onDataChange],
	);

	const removeItem = useCallback(
		(itemId: string | number) => {
			if (mode === "controlled") {
				const newData = controlledData.filter((item) => item.id !== itemId);
				onDataChange?.(newData);
			} else {
				setInternalData((prev) => prev.filter((item) => item.id !== itemId));
			}
		},
		[mode, controlledData, onDataChange],
	);

	const handleSort = useCallback(
		(key: string) => {
			let direction: Direction = "asc";
			if (sortConfig.key === key && sortConfig.direction === "asc") {
				direction = "desc";
			}
			setSortConfig({ key, direction });
		},
		[sortConfig],
	);

	// Get current effective data
	const data = getEffectiveData();

	// Data processing
	const getSortedData = (): any[] => {
		let filteredData = [...data];
		const searchTermLower = searchTerm.toLowerCase();

		// Filter by search term
		if (searchTermLower && columns.some((col: TableColumn) => col.searchable)) {
			filteredData = filteredData.filter((item: any): boolean => {
				return columns.some((column: TableColumn): boolean => {
					if (!column.searchable) return false;
					let value: string;
					if (column.searchFields) {
						if (typeof column.searchFields === "function") {
							value = column.searchFields(item[column.key]);
						} else {
							const fields: string[] = normaliseList(column.searchFields);
							value = fields
								.map((field: string): any => item[field])
								.filter((val: any): boolean => val != null)
								.join(" ");
						}
					} else {
						value = item[column.key];
					}
					return value?.toString().toLowerCase().includes(searchTermLower);
				});
			});
		}

		// Sort data
		if (sortConfig.key) {
			filteredData.sort((a: any, b: any) => {
				const column = columns.find((col: TableColumn) => col.key === sortConfig.key);
				let aValue: any, bValue: any;
				if (!column) return 0;

				if (typeof column.sortField === "function") {
					aValue = column.sortField(a);
					bValue = column.sortField(b);
				} else if (typeof column.sortField === "string" || Array.isArray(column.sortField)) {
					const sortFields: string[] = normaliseList(column.sortField);
					aValue = sortFields
						.map((field: string) => accessAttribute(a, field))
						.reduce((acc, val) => acc + (val ?? ""), "");
					bValue = sortFields
						.map((field: string) => accessAttribute(b, field))
						.reduce((acc, val) => acc + (val ?? ""), "");
				} else {
					aValue = a[column.key];
					bValue = b[column.key];
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
	const handleRowClick = (event: MouseEvent<HTMLTableRowElement>, item: any): void => {
		if (contextMenu) return;

		const isInteractiveElement = (element: Element | null): boolean => {
			if (!element) return false;
			const tagName = element.tagName?.toLowerCase();
			return (
				["button", "a", "input", "select", "textarea"].includes(tagName) ||
				!!(element as HTMLElement).onclick ||
				element.getAttribute("onclick") !== null ||
				element.classList?.contains("clickable-badge") ||
				element.classList?.contains("btn") ||
				(element as HTMLElement).style?.cursor === "pointer"
			);
		};

		let currentElement: Element | null = event.target as Element;
		while (currentElement && currentElement !== event.currentTarget) {
			if (isInteractiveElement(currentElement)) return;
			currentElement = currentElement.parentElement;
		}

		openViewModal(item);
	};

	const handleRowRightClick = (item: any, event: MouseEvent<HTMLTableRowElement>): void => {
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
		nameKey: nameKey,
		itemType: itemType,
	});

	// Context menu handlers
	const handleContextAction = (action: string, e: MouseEvent): void => {
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
	const handleEditSuccess = (updatedItem: any): void => {
		updateItem(updatedItem);
		closeEditModal();
	};

	const handleAddSuccess = (newItem: any): void => {
		addItem(newItem);
		closeAddModal();
	};

	// Close context menu on outside click or escape
	useEffect(() => {
		const handleGlobalClick = (): void => {
			if (contextMenu) {
				setContextMenu(null);
			}
		};
		const handleKeyPress = (e: KeyboardEvent): void => {
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

	// Pagination
	const sortedData = getSortedData();
	const totalPages = Math.ceil(sortedData.length / pageSize);
	const startIndex = showAllEntries ? 0 : currentPage * pageSize;
	const endIndex = showAllEntries ? sortedData.length : startIndex + pageSize;
	const currentPageData = sortedData.slice(startIndex, endIndex);

	useEffect(() => setCurrentPage(0), [searchTerm, data]);

	const goToPage = (page: number): void => setCurrentPage(Math.max(0, Math.min(totalPages - 1, page)));
	const handlePageSizeChange = (newPageSize: number): void => {
		setPageSize(newPageSize);
		setCurrentPage(0);
	};

	if (error) {
		return <div className="alert alert-danger mt-3">{error}</div>;
	}

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
							onChange={(e) => setSearchTerm(e.target.value)}
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
						{...(compact ? { size: "sm" as const } : {})}
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
								className={`table-row-clickable`}
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
										{renderViewField(column, item, `table-row-${item.id}`)}
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
			{!showAllEntries && data.length > 19 && (
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
						borderRadius: "8px",
						boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
						padding: "4px 0",
						minWidth: compact ? "120px" : "150px",
						overflow: "hidden",
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
							onMouseEnter={(e) => ((e.target as HTMLElement).style.backgroundColor = "#f8f9fa")}
							onMouseLeave={(e) => ((e.target as HTMLElement).style.backgroundColor = "white")}
							id={id}
						>
							<i className={`bi bi-${icon} me-2`}></i>
							{text}
						</div>
					))}
				</div>
			)}

			{children ? children(getEffectiveData()) : null}

			<Modal
				show={showModal}
				onHide={closeAddModal}
				onSuccess={handleAddSuccess}
				size={modalSize}
				data={{}}
				submode="add"
				{...modalProps}
			/>

			<Modal
				show={showEditModal}
				onHide={closeEditModal}
				onSuccess={handleEditSuccess}
				data={selectedItem || {}}
				submode="edit"
				onDelete={removeItem}
				size={modalSize}
				{...modalProps}
			/>

			<Modal
				show={showViewModal}
				onHide={() => {
					updateItem(selectedItem); // Todo
					closeViewModal();
				}}
				onSuccess={handleEditSuccess}
				data={selectedItem}
				submode="view"
				onDelete={removeItem}
				onEdit={() => {
					closeViewModal();
					openEditModal(selectedItem);
				}}
				size={modalSize}
				{...modalProps}
			/>

			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</div>
	);
};

export default GenericTable;
