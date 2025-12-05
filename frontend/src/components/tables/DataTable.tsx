import React, { MouseEvent, ReactNode, useCallback, useEffect, useState } from "react";
import { Button, Form } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { EntityType, JamData, useDataContext } from "../../contexts/DataContext";
import { api } from "../../services/Api";
import { getTableIcon } from "../rendering/view/Icons";
import { RenderViewFieldWithContext } from "../rendering/view/ViewRenders";
import { accessAttribute } from "../../utils/Utils";
import useModalState from "../../hooks/useModalState";
import { pluralize } from "../../utils/StringUtils";
import { TableColumn } from "../rendering/view/TableColumns";
import { useActiveHandler, useDeleteHandler } from "../../utils/DeleteHandler";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { ContextMenu, ContextMenuState, MenuItem } from "./ContextMenu";
import "./DataTable.css";
import LoadingSpinner from "../spinner/Spinner";

export type Direction = "asc" | "desc";

export interface SortConfig {
	key: string;
	direction: Direction;
}

export interface DataTableProps {
	data?: any | null;
	columns?: TableColumn[];
	onDataChange?: (data: any[]) => void;
	error?: string | null;
	showAdd?: boolean;
	menuItems?: string[];
}

export interface GenericTableProps {
	// Data source - entity type from DataContext
	entityType: EntityType;
	data?: any[];

	// Mode
	mode?: "default" | "import";

	// Optional endpoint when data are not provided or not fetched from context
	endpoint?: string;

	// Table configuration
	columns?: TableColumn[];
	initialSortConfig?: Partial<SortConfig>;
	menuItems?: string[];

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

	// Import mode configuration
	onImportSuccess?: (importedItem: any) => Promise<any>;

	// Additional content
	children?: (data: any[]) => ReactNode;
}

export const DataTable: React.FC<GenericTableProps> = ({
	entityType,
	mode = "default",
	data: providedData,
	endpoint = "",
	columns = [],
	initialSortConfig = {},
	Modal,
	modalSize = "lg",
	modalProps = {},
	nameKey,
	itemType,
	title,
	showAllEntries = false,
	emptyMessage,
	compact = false,
	showSearch = true,
	showAdd = true,
	onImportSuccess,
	children,
	menuItems,
}: GenericTableProps) => {
	const { token } = useAuth();

	// Data management
	const dataContext = useDataContext();
	const [isLoading, setIsLoading] = useState<boolean>(false);
	const [loadError, setLoadError] = useState<string | null>(null);
	const [fetchedData, setFetchedData] = useState<any[]>([]);
	const [debouncedSearchTerm, setDebouncedSearchTerm] = useState<string>("");

	// Search and sort
	const [sortConfig, setSortConfig] = useState<SortConfig>(
		(initialSortConfig as SortConfig) || { key: "created_at", direction: "desc" },
	);
	const [searchTerm, setSearchTerm] = useState<string>("");

	// UI state
	const { showToastSuccess, showToastError } = useGlobalToast();
	const [contextMenu, setContextMenu] = useState<ContextMenuState | null>(null);
	const [currentPage, setCurrentPage] = useState<number>(0);
	const [pageSize, setPageSize] = useState<number>(20);
	const [totalCount, setTotalCount] = useState<number>(0);

	const isServerPagination = !!endpoint && !providedData;

	const {
		showModal,
		showViewModal,
		showEditModal,
		showImportModal,
		selectedItem,
		openAddModal,
		closeAddModal,
		openViewModal,
		closeViewModal,
		openEditModal,
		closeEditModal,
		openImportModal,
		closeImportModal,
	} = useModalState();

	useEffect(() => {
		const timer = setTimeout(() => {
			setDebouncedSearchTerm(searchTerm);
		}, 300); // Wait 300ms after user stops typing

		return () => clearTimeout(timer);
	}, [searchTerm]);

	// Reset page when debounced search changes
	useEffect(() => {
		if (isServerPagination) {
			setCurrentPage(0);
		}
	}, [debouncedSearchTerm, isServerPagination]);

	const fetchData = async () => {
		setIsLoading(true);
		setLoadError(null);

		try {
			const params = new URLSearchParams({
				page: currentPage.toString(),
				page_size: pageSize.toString(),
				sort_by: sortConfig.key,
				sort_direction: sortConfig.direction,
				search: debouncedSearchTerm,
			});

			const response: any = await api.get(`${endpoint}/paged?${params.toString()}`, token);
			setFetchedData(response.items);
			setTotalCount(response.total);
		} catch (error: any) {
			setLoadError(error.message || "Failed to load data");
		} finally {
			setIsLoading(false);
		}
	};

	useEffect(() => {
		if (isServerPagination) {
			fetchData().then((_) => null);
		}
	}, [endpoint, token, currentPage, pageSize, sortConfig, isServerPagination, debouncedSearchTerm]);

	useEffect(() => {
		if (!isServerPagination) {
			setCurrentPage(0);
		}
	}, [searchTerm, isServerPagination, sortConfig]);

	const getData = (): any[] => {
		if (providedData !== undefined) {
			return providedData;
		}
		if (isServerPagination) {
			return fetchedData;
		}
		return (dataContext as any)[entityType] || [];
	};

	useEffect(() => {
		if (loadError) {
			showToastError(`Failed to load ${itemType}s`);
		}
	}, [loadError, itemType, showToastError]);

	const data: JamData[] = getData();
	const { error: contextError } = dataContext;

	// CRUD operations using context methods
	const addItem = useCallback(
		(newItem: any) => {
			dataContext.addEntity(entityType, newItem);
		},
		[dataContext, entityType],
	);

	const updateItem = useCallback(
		(updatedItem: any) => {
			if (updatedItem) {
				dataContext.updateEntity(entityType, updatedItem.id, updatedItem);
			}
		},
		[dataContext, entityType],
	);

	const removeItem = useCallback(
		(itemId: number) => {
			dataContext.deleteEntity(entityType, itemId);
		},
		[dataContext, entityType],
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

	// Data processing
	const getSortedData = (): JamData[] => {
		let filteredData: JamData[] = [...data];
		const searchTermLower: string = searchTerm.toLowerCase();

		// Filter by search term
		if (searchTermLower && columns.some((col: TableColumn): boolean | undefined => col.searchable)) {
			filteredData = filteredData.filter((item: JamData): boolean => {
				return columns.some((column: TableColumn): boolean | undefined => {
					if (!column.searchable) return false;
					let value: string | null | Date | number;
					if (column.searchFields) {
						if (typeof column.searchFields === "function") {
							value = column.searchFields(item, dataContext);
						} else {
							value = accessAttribute(item, column.searchFields);
						}
					} else {
						value = item[column.key as keyof JamData];
					}
					return value?.toString().toLowerCase().includes(searchTermLower);
				});
			});
		}

		// Sort data
		if (sortConfig.key) {
			filteredData.sort((a: any, b: any) => {
				const column: TableColumn | undefined = columns.find(
					(col: TableColumn): boolean => col.key === sortConfig.key,
				);
				let aValue: any, bValue: any;
				if (!column) return 0;

				if (typeof column.sortField === "function") {
					aValue = column.sortField(a, dataContext);
					bValue = column.sortField(b, dataContext);
				} else if (typeof column.sortField === "string") {
					aValue = a[column.sortField];
					bValue = b[column.sortField];
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

		// Different behavior based on mode
		if (mode === "import") {
			openImportModal(item);
		} else {
			openViewModal(item);
		}
	};

	const handleRowRightClick = (item: any, event: MouseEvent<HTMLTableRowElement>): void => {
		event.preventDefault();
		event.stopPropagation();
		setContextMenu({ item, x: event.clientX, y: event.clientY, show: true });
	};

	const activeHandler = useActiveHandler({
		entityType,
		nameKey,
		itemType,
	});
	const deleteHandler = useDeleteHandler({
		entityType,
		nameKey,
		itemType,
	});

	// Select the handler based on mode
	const handleDelete = mode === "import" ? activeHandler : deleteHandler;

	// Success handlers
	const handleEditSuccess = (updatedItem: any): void => {
		updateItem(updatedItem);
		closeEditModal();
	};

	const handleAddSuccess = (newItem: any): void => {
		addItem(newItem);
		closeAddModal();
	};

	const handleImportSuccess = (importedItem: any): void => {
		onImportSuccess?.(importedItem).then((_) => {
			fetchData().then((_) => {
				showToastSuccess("Job imported successfully.");
				closeImportModal();
			});
		});
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

	// Pagination calculations
	const sortedData = isServerPagination ? data : getSortedData();
	let currentPageData: any[];
	let totalPages: number;
	let displayTotal: number;

	if (isServerPagination) {
		// Server-side: data already paginated
		currentPageData = sortedData;
		displayTotal = totalCount;
		totalPages = Math.ceil(totalCount / pageSize);
	} else {
		// Client-side: do pagination ourselves
		displayTotal = sortedData.length;
		totalPages = Math.ceil(displayTotal / pageSize);

		if (showAllEntries) {
			currentPageData = sortedData;
		} else {
			const startIndex = currentPage * pageSize;
			const endIndex = startIndex + pageSize;
			currentPageData = sortedData.slice(startIndex, endIndex);
		}
	}

	useEffect(() => setCurrentPage(0), [searchTerm]);

	const handleSnoozeItem = (weeks: number) => {
		return async (item: any) => {
			try {
				const snoozeDate = new Date();
				snoozeDate.setDate(snoozeDate.getDate() + weeks * 7);

				const updatedItem = await api.put(
					`${endpoint || entityType}/${item.id}`,
					{ followup_snooze_datetime: snoozeDate.toISOString() },
					token,
				);
				updateItem(updatedItem);
				showToastSuccess(`${item.title} was snoozed for ${weeks} week(s).`);
			} catch (error) {
				showToastError(`Failed to snooze ${item.title}. Please try again.`);
			} finally {
				setContextMenu(null);
			}
		};
	};

	// Get context menu items based on mode
	const getContextMenuItems = () => {
		let baseItems: MenuItem[] = [
			{ action: "view", icon: "eye", text: "View", id: "context-menu-view", function: openViewModal },
			{ action: "edit", icon: "pencil", text: "Edit", id: "context-menu-edit", function: openEditModal },
			{
				action: "snooze",
				icon: "alarm",
				text: "Snooze for...",
				id: "context-menu-snooze",
				hasSubmenu: true,
				submenu: [
					{ action: "snooze-1", text: "1 week", function: handleSnoozeItem(1) },
					{ action: "snooze-2", text: "2 weeks", function: handleSnoozeItem(2) },
					{ action: "snooze-3", text: "3 weeks", function: handleSnoozeItem(3) },
					{ action: "snooze-4", text: "4 weeks", function: handleSnoozeItem(4) },
				],
			},
			{
				action: "import",
				icon: "upload",
				text: "Import",
				id: "context-menu-import",
				function: openImportModal,
			},
			{
				action: "delete",
				icon: "trash",
				text: "Delete",
				id: "context-menu-delete",
				color: "#dc3545",
				function: handleDelete,
			},
		];

		if (!menuItems) {
			if (mode === "import") {
				menuItems = ["import", "delete"];
			} else {
				menuItems = ["view", "edit", "delete"];
			}
		}
		baseItems = baseItems.filter((item: MenuItem): boolean => menuItems!.includes(item.action));

		return baseItems;
	};

	// Get button text based on mode
	const getAddButtonText = () => {
		if (mode === "import") {
			return `Import ${itemType}`;
		} else {
			return `Add ${itemType}`;
		}
	};

	// Get button icon based on mode
	const getAddButtonIcon = () => {
		if (mode === "import") {
			return "bi-upload";
		}
		return "bi-plus-circle";
	};

	if (contextError) {
		return <div className="alert alert-danger mt-3">{contextError.message}</div>;
	}

	if (loadError) {
		return (
			<div className="alert alert-danger mt-3">
				<i className="bi bi-exclamation-triangle-fill me-2"></i>
				{loadError}
			</div>
		);
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
					<div className="d-flex align-items-center gap-3" style={{ width: showAdd ? "40%" : "100%" }}>
						<input
							type="text"
							className="form-control"
							placeholder="Search..."
							value={searchTerm}
							onChange={(e): void => setSearchTerm(e.target.value)}
							id="search-input"
						/>
						<span className="text-muted small" style={{ whiteSpace: "nowrap" }}>
							Showing {displayTotal} Entries
						</span>
					</div>
				)}
				{showAdd && mode !== "import" && (
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
						<i className={`${getAddButtonIcon()} me-2`} style={{ fontSize: "1.1rem" }}></i>
						{getAddButtonText()}
					</Button>
				)}
			</div>

			{/* Table */}
			{isLoading ? (
				<LoadingSpinner text="Loading..." />
			) : (
				<>
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
												<RenderViewFieldWithContext
													field={column}
													item={item}
													id={`table-row-${item.id}`}
												/>
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
					{!showAllEntries && displayTotal > 20 && (
						<div className={`d-flex justify-content-between align-items-center mt-0`}>
							<div className="d-flex align-items-center gap-0">
								{[
									{
										action: () => setCurrentPage(0),
										disabled: currentPage === 0,
										icon: "chevron-double-left",
										label: "First",
									},
									{
										action: () => setCurrentPage(Math.max(0, currentPage - 1)),
										disabled: currentPage === 0,
										icon: "chevron-left",
										label: "Previous",
									},
									{
										action: () => setCurrentPage(Math.min(totalPages - 1, currentPage + 1)),
										disabled: currentPage >= totalPages - 1,
										icon: "chevron-right",
										label: "Next",
									},
									{
										action: () => setCurrentPage(totalPages - 1),
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
								{isServerPagination && (
									<span
										className={`small text-muted text-nowrap`}
										style={compact ? { fontSize: "0.75rem" } : {}}
									>
										{currentPage * pageSize + 1} to{" "}
										{Math.min((currentPage + 1) * pageSize, totalCount)} of {totalCount}
									</span>
								)}
								<span
									className={`small text-muted text-nowrap`}
									style={compact ? { fontSize: "0.75rem" } : {}}
								>
									Page {currentPage + 1} of {totalPages || 1}
								</span>
								<Form.Select
									size="sm"
									id="page-items-select"
									value={pageSize}
									onChange={(e) => {
										setPageSize(Number(e.target.value));
										setCurrentPage(0); // Reset to first page
									}}
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
				</>
			)}

			{/* Context Menu */}
			{contextMenu?.show && (
				<ContextMenu
					position={{ x: contextMenu.x, y: contextMenu.y }}
					items={getContextMenuItems()}
					selectedItem={contextMenu.item}
					onClose={() => setContextMenu(null)}
					onItemClick={(menuItem, item) => {
						if (menuItem.function) {
							menuItem.function(item);
						}
					}}
					compact={compact}
				/>
			)}

			{children ? children(data) : null}

			{mode !== "import" && (
				<>
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
						onHide={closeViewModal}
						onSuccess={updateItem}
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
				</>
			)}

			{mode === "import" && (
				<Modal
					show={showImportModal}
					onHide={closeImportModal}
					onSuccess={handleImportSuccess}
					onDelete={removeItem}
					data={selectedItem}
					submode="import"
					size={modalSize}
					{...modalProps}
				/>
			)}
		</div>
	);
};

export default DataTable;
