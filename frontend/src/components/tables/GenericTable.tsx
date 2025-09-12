import React, { MouseEvent, ReactNode, useCallback, useEffect, useState } from "react";
import { Button, Form } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { api } from "../../services/Api";
import { getTableIcon, renderViewElement } from "../rendering/view/ViewRenders";
import { accessAttribute } from "../../utils/Utils";
import AlertModal from "../modals/AlertModal";
import useModalState from "../../hooks/useModalState";
import useGenericAlert from "../../hooks/useGenericAlert";
import { pluralize } from "../../utils/StringUtils";
import { TableColumn } from "../rendering/view/TableColumnRenders";
import "./GenericTable.css";
import { viewFields } from "../rendering/view/ModalFieldRenders";

export interface SortConfig {
	key: string;
	direction: "asc" | "desc";
}

export interface ContextMenuState {
	item: any;
	x: number;
	y: number;
	show: boolean;
}

export interface UseTableDataResult {
	data: any[];
	setData: React.Dispatch<React.SetStateAction<any[]>>;
	loading: boolean;
	error: string | null;
	sortConfig: SortConfig;
	setSortConfig: React.Dispatch<React.SetStateAction<SortConfig>>;
	searchTerm: string;
	setSearchTerm: React.Dispatch<React.SetStateAction<string>>;
	addItem: (newItem: any) => void;
	updateItem: (updatedItem: any) => void;
	removeItem: (itemId: string | number) => void;
	refetch: () => Promise<void>;
}

export interface CreateGenericDeleteHandlerProps {
	endpoint: string;
	token: string | null;
	showDelete: (config: any) => Promise<boolean>;
	showError: (config: any) => Promise<boolean>;
	removeItem?: (itemId: string | number) => void;
	setData?: React.Dispatch<React.SetStateAction<any[]>>;
	nameKey: string;
	itemType?: string;
}

export interface TableProps {
	onChange?: () => void;
	data?: any[] | null;
	columns?: TableColumn[];
}

export interface GenericTableWithModalsProps {
	// Table data
	data?: any[];
	columns?: TableColumn[];
	loading?: boolean;
	error?: string | null;

	// Search and sort
	searchTerm?: string;
	onSearchChange?: (searchTerm: string) => void;
	sortConfig?: SortConfig;
	onSort?: (config: SortConfig) => void;

	// Modal configuration
	Modal: React.ComponentType<any>;
	modalSize?: string;
	modalProps?: any;

	// Data management
	endpoint: string;
	nameKey: string;
	itemType: string;
	addItem: (newItem: any) => void;
	updateItem: (updatedItem: any) => void;
	removeItem: (itemId: string | number) => void;
	setData: React.Dispatch<React.SetStateAction<any[]>>;

	// Display options
	title?: string;
	showAllEntries?: boolean;
	emptyMessage?: string;
	compact?: boolean;
	showSearch?: boolean;
	showAdd?: boolean;

	// Additional content
	children?: ReactNode;
}

const useBaseTableData = (
	customSortConfig: Partial<SortConfig> = {},
): {
	data: any[];
	setData: React.Dispatch<React.SetStateAction<any[]>>;
	loading: boolean;
	setLoading: React.Dispatch<React.SetStateAction<boolean>>;
	error: string | null;
	setError: React.Dispatch<React.SetStateAction<string | null>>;
	sortConfig: SortConfig;
	setSortConfig: React.Dispatch<React.SetStateAction<SortConfig>>;
	searchTerm: string;
	setSearchTerm: React.Dispatch<React.SetStateAction<string>>;
	addItem: (newItem: any) => void;
	updateItem: (updatedItem: any) => void;
	removeItem: (itemId: string | number) => void;
} => {
	const [data, setData] = useState<any[]>([]);
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<string | null>(null);
	const [sortConfig, setSortConfig] = useState<SortConfig>(
		(customSortConfig as SortConfig) || { key: "created_at", direction: "desc" },
	);
	const [searchTerm, setSearchTerm] = useState<string>("");

	const addItem = useCallback((newItem: any) => setData((prev) => [newItem, ...prev]), []);
	const updateItem = useCallback(
		(updatedItem: any) => setData((prev) => prev.map((item) => (item.id === updatedItem.id ? updatedItem : item))),
		[],
	);
	const removeItem = useCallback(
		(itemId: string | number) => setData((prev) => prev.filter((item) => item.id !== itemId)),
		[],
	);

	return {
		data,
		setData,
		loading,
		setLoading,
		error,
		setError,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	};
};

export const useProvidedTableData = (
	providedData: any[] | null = null,
	customSortConfig: Partial<SortConfig> = {},
): UseTableDataResult => {
	const base = useBaseTableData(customSortConfig);

	// Update data when providedData changes
	useEffect(() => {
		base.setData(providedData || []);
		base.setLoading(false);
		base.setError(null);
	}, [providedData, base.setData, base.setLoading, base.setError]);

	const refetch = useCallback(async () => {}, []);

	return {
		...base,
		refetch,
	};
};

export const useTableData = (
	endpoint: string,
	dependencies: any[] = [],
	queryParams: Record<string, any> = {},
	customSortConfig: Partial<SortConfig> = {},
): UseTableDataResult => {
	const { token } = useAuth();
	const base = useBaseTableData(customSortConfig);

	// API fetch function
	const fetchData = useCallback(async (): Promise<void> => {
		base.setLoading(true);
		base.setError(null);

		try {
			const queryString =
				Object.keys(queryParams).length > 0 ? "?" + new URLSearchParams(queryParams).toString() : "";
			const result = await api.get(`${endpoint}/${queryString}`, token);
			base.setData(result || []);
		} catch (err) {
			console.error(`Error fetching ${endpoint}:`, err);
			base.setError(`Failed to load ${endpoint}. Please try again later.`);
			base.setData([]);
		} finally {
			base.setLoading(false);
		}
	}, [endpoint, token, JSON.stringify(queryParams), base.setData, base.setLoading, base.setError]);

	// Fetch data when dependencies change
	useEffect(() => {
		if (token) {
			fetchData().then(() => {});
		}
	}, [token, fetchData, ...dependencies]);

	return {
		...base,
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

export const GenericTableWithModals: React.FC<GenericTableWithModalsProps> = ({
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
	Modal,
	modalSize = "lg",
	modalProps = {},

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
	emptyMessage,
	compact = false,
	showSearch = true,
	showAdd = true,

	// Additional content
	children,
}) => {
	const { token } = useAuth();
	const { alertState, showDelete, showError, hideAlert } = useGenericAlert();
	const [contextMenu, setContextMenu] = useState<ContextMenuState | null>(null);
	const [currentPage, setCurrentPage] = useState<number>(0);
	const [pageSize, setPageSize] = useState<number>(20);
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

	const getEffectiveItem = (item: any, column: TableColumn): any => {
		if (!column || !column.accessKey) return item;
		return accessAttribute(item, column.accessKey);
	};

	const getColumnValue = (item: any, column: TableColumn, field?: string): any => {
		if (!column) return null;
		const effectiveItem = getEffectiveItem(item, column);
		if (field) return accessAttribute(effectiveItem, field);
		return accessAttribute(effectiveItem, column.key);
	};

	// Data processing
	const getSortedData = (): any[] => {
		let filteredData = [...data];

		// Filter by search term
		if (searchTerm && columns.some((col) => col.searchable)) {
			const searchTermLower = searchTerm.toLowerCase();
			filteredData = filteredData.filter((item) => {
				return columns.some((column) => {
					if (!column.searchable) return false;
					let value: string;
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
				let aValue: any, bValue: any;

				if (column?.sortField) {
					aValue = getColumnValue(a, column, column.sortField);
					bValue = getColumnValue(b, column, column.sortField);
				} else {
					aValue = getColumnValue(a, column!);
					bValue = getColumnValue(b, column!);
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
	const handleSort = (key: string): void => {
		let direction: "asc" | "desc" = "asc";
		if (sortConfig.key === key && sortConfig.direction === "asc") {
			direction = "desc";
		}
		onSort({ key, direction });
	};

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
		setData: setData,
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
										{renderViewElement(column, item, `table-row-${item.id}`)}
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

			{children}
			<Modal
				show={showModal}
				onHide={closeAddModal}
				onSuccess={handleAddSuccess}
				size={modalSize}
				data={{}}
				submode="add"
			/>

			<Modal
				show={showEditModal}
				onHide={closeEditModal}
				onSuccess={handleEditSuccess}
				data={selectedItem || {}}
				submode="edit"
				size={modalSize}
			/>

			<Modal
				show={showViewModal}
				onHide={closeViewModal}
				onSuccess={handleEditSuccess}
				data={selectedItem}
				submode="view"
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

export default GenericTableWithModals;
