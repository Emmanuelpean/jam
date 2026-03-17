import React, {
	forwardRef,
	JSX,
	MouseEvent,
	ReactNode,
	useCallback,
	useEffect,
	useImperativeHandle,
	useRef,
	useState,
} from "react";
import { Button, Form } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import {
	DataContextValue,
	EntityType,
	entityTypeToGenericName,
	JamData,
	useDataContext,
} from "../../contexts/DataContext";
import { ApiResponse, baseApi } from "../../services/api/Base";
import { getTableIcon } from "../rendering/view/Icons";
import { RenderViewFieldWithContext } from "../rendering/view/ViewRenders";
import { accessAttribute } from "../../utils/Utils";
import { pluralize } from "../../utils/StringUtils";
import { TableColumn } from "../rendering/view/TableColumns";
import {
	useActivateEntity,
	useDeactivateEntity,
	useDeactivateEntityConfirm,
	useDeleteEntityConfirm,
} from "../../utils/DeleteHandler";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { MenuItem } from "../ContextMenu/ContextMenu";
import LoadingSpinner from "../Spinner/Spinner";
import { DataModalHandle, modalModes } from "../DataModal/DataModal";
import { EnrichedJobData, JobData } from "../../services/schemas/DataTables";
import "./DataTable.scss";
import FollowUpModal, { FollowUpModalHandle } from "../FollowUpModal/FollowUpModal";
import { useContextMenu } from "../../contexts/ContextMenuContext";
import PageHeader from "../../pages/PageHeader/PageHeader";

export type Direction = "asc" | "desc";

export interface SortConfig {
	key: string;
	direction: Direction;
}

export interface DataTableProps {
	data?: any | null;
	columns?: TableColumn[];
	showAdd?: boolean;
	menuItems?: string[] | ((item: any) => string[]);
	title?: string;
	onTotalCountChange?: (count: number) => void;
	onSuccess?: () => void;
	reloadTrigger?: number;
	modalProps?: any;
}

export interface GenericTableProps {
	// Data source - entity type from DataContext
	entityType: EntityType;
	data?: JamData[];

	// Mode
	mode?: "default" | "import";

	// Optional endpoint when data are not provided or not fetched from context
	endpoint?: string;

	// Table configuration
	columns?: TableColumn[];
	initialSortConfig?: Partial<SortConfig>;
	menuItems?: string[] | ((item: any) => string[]);
	rowMode?: (item: any) => "default" | "import";

	// Modal configuration
	Modal: React.ComponentType<any>;
	modalSize?: string;
	modalProps?: any;
	defaultModalMode?: modalModes;

	// Data management
	initialData?: any;

	// Display options
	title?: string;
	showAllEntries?: boolean;
	emptyMessage?: string;
	compact?: boolean;
	showSearch?: boolean;
	showAdd?: boolean;

	// Additional content
	children?: (data: any[]) => ReactNode;
	toolbarAddon?: React.ReactNode;
	reloadTrigger?: number;
	queryParams?: Record<string, string>;
	onTotalCountChange?: (count: number) => void;
	onSuccess?: () => void;
}

export interface DataTableHandle {
	openAddModal: (data?: any) => void;
}

export const DataTable = forwardRef<DataTableHandle, GenericTableProps>(
	(
		{
			entityType,
			mode = "default",
			data: providedData,
			endpoint = "",
			columns = [],
			initialSortConfig = {},
			Modal,
			modalSize = "lg",
			modalProps = {},
			title,
			showAllEntries = false,
			emptyMessage,
			compact = false,
			showSearch = true,
			showAdd = true,
			initialData = {},
			children,
			menuItems,
			rowMode,
			toolbarAddon,
			reloadTrigger,
			queryParams,
			defaultModalMode = "view",
			onTotalCountChange,
			onSuccess,
		}: GenericTableProps,
		ref
	): JSX.Element => {
		const { token } = useAuth();
		const modalRef = useRef<DataModalHandle>(null);
		const openViewModal = (item: any): void | undefined => modalRef.current?.showView(item);
		const openEditModal = (item: any): void | undefined => modalRef.current?.showEdit(item);
		const openAddModal = (data?: any) => modalRef.current?.showAdd(data ?? initialData);
		const openImportModal = (item: any): void | undefined => modalRef.current?.showImport(item);

		useImperativeHandle(ref, () => ({ openAddModal }));

		// Add context menu hook
		const { openContextMenu } = useContextMenu();

		// Data management
		const dataContext: DataContextValue = useDataContext();
		const [isLoading, setIsLoading] = useState<boolean>(false);
		const [loadError, setLoadError] = useState<string | null>(null);
		const [fetchedData, setFetchedData] = useState<any[]>([]);
		const [debouncedSearchTerm, setDebouncedSearchTerm] = useState<string>("");

		// Search and sort
		const [sortConfig, setSortConfig] = useState<SortConfig>(
			(initialSortConfig as SortConfig) || { key: "created_at", direction: "desc" }
		);
		const [searchTerm, setSearchTerm] = useState<string>("");

		// UI state
		const { showToastSuccess, showToastError } = useGlobalToast();
		const [currentPage, setCurrentPage] = useState<number>(0);
		const [pageSize, setPageSize] = useState<number>(20);
		const [totalCount, setTotalCount] = useState<number>(0);
		const [totalFilteredCount, setTotalFilteredCount] = useState<number>(0);
		const [showSpinner, setShowSpinner] = useState<boolean>(false);

		useEffect(() => {
			onTotalCountChange?.(totalCount);
		}, [totalCount, onTotalCountChange]);
		const followUpModalRef = useRef<FollowUpModalHandle>(null);

		useEffect(() => {
			if (!isLoading) {
				setShowSpinner(false);
				return;
			}
			const timer = setTimeout(() => setShowSpinner(true), 200);
			return () => clearTimeout(timer);
		}, [isLoading]);

		const isServerPagination: boolean = !!endpoint && !providedData;

		const entityName: string = entityTypeToGenericName(entityType);

		useEffect(() => {
			const timer = setTimeout((): void => {
				setDebouncedSearchTerm(searchTerm);
			}, 300); // Wait 300ms after user stops typing
			return (): void => clearTimeout(timer);
		}, [searchTerm]);

		// Reset page when debounced search changes
		useEffect(() => {
			setCurrentPage(0);
		}, [debouncedSearchTerm, sortConfig, pageSize]);

		const fetchData = async (): Promise<void> => {
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

				if (queryParams) {
					Object.entries(queryParams).forEach(([key, value]) => {
						params.set(key, value);
					});
				}

				const response: ApiResponse = await baseApi.get(`${endpoint}/paged?${params.toString()}`, token);
				setFetchedData(response.data.items);
				setTotalCount(response.data.total);
				setTotalFilteredCount(response.data.total_filtered);
			} catch (error: any) {
				setLoadError(error.message || "Failed to load data");
			} finally {
				setIsLoading(false);
			}
		};

		useEffect(() => {
			if (isServerPagination) {
				fetchData().then(() => null);
			}
		}, [reloadTrigger]);

		useEffect((): void => {
			if (isServerPagination) {
				fetchData().then((_): null => null);
			}
		}, [endpoint, token, currentPage, pageSize, sortConfig, isServerPagination, debouncedSearchTerm, queryParams]);

		const getData = (): JamData[] => {
			if (providedData !== undefined) {
				return providedData;
			}
			if (isServerPagination) {
				return fetchedData;
			}
			return dataContext.getEntityData(entityType);
		};

		const data: JamData[] = getData();
		const { error: contextError } = dataContext;

		const handleSort = useCallback(
			(key: string): void => {
				let direction: Direction = "asc";
				if (sortConfig.key === key && sortConfig.direction === "asc") {
					direction = "desc";
				}
				setSortConfig({ key, direction });
			},
			[sortConfig]
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
				filteredData.sort((a: any, b: any): 0 | 1 | -1 => {
					const column: TableColumn | undefined = columns.find(
						(col: TableColumn): boolean => col.key === sortConfig.key
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

			if ((rowMode ? rowMode(item) : mode) === "import") {
				openImportModal(item);
			} else {
				if (defaultModalMode === "edit") {
					openEditModal(item);
				} else {
					openViewModal(item);
				}
			}
		};

		const activeHandler: (item: JamData) => Promise<boolean> = useDeactivateEntityConfirm(entityType);
		const deleteHandler: (item: JamData) => Promise<boolean> = useDeleteEntityConfirm(entityType);
		const activateEntityHandler: (item: JamData) => Promise<boolean> = useActivateEntity(entityType);
		const deactivateEntityHandler: (item: JamData) => Promise<boolean> = useDeactivateEntity(entityType);

		const handleDelete = async (item: JamData): Promise<boolean> => {
			let result: boolean;
			if (mode === "import") {
				result = await activeHandler(item);
			} else {
				result = await deleteHandler(item);
			}
			if (result && isServerPagination) {
				fetchData().then((_): null => null);
			}
			return result;
		};

		const handleSuccess = (): void => {
			if (isServerPagination) {
				fetchData().then((): null => null);
			}
			showToastSuccess("Job imported successfully.");
			onSuccess?.();
		};

		const handleDeleteSuccess = (): void => {
			if (isServerPagination) {
				fetchData().then((): null => null);
			}
			onSuccess?.();
		};

		// Pagination calculations
		const sortedData: JamData[] = isServerPagination ? data : getSortedData();
		let currentPageData: any[];
		let totalPages: number;

		if (isServerPagination) {
			// Server-side: data already paginated
			currentPageData = sortedData;
			totalPages = Math.ceil(totalFilteredCount / pageSize);
		} else {
			// Client-side: do pagination ourselves
			totalPages = Math.ceil(sortedData.length / pageSize);

			if (showAllEntries) {
				currentPageData = sortedData;
			} else {
				const startIndex: number = currentPage * pageSize;
				const endIndex: number = startIndex + pageSize;
				currentPageData = sortedData.slice(startIndex, endIndex);
			}
		}

		useEffect(() => {
			if (!isServerPagination) {
				setTotalFilteredCount(sortedData.length);
			}
		}, [sortedData, isServerPagination]);

		useEffect(() => {
			if (!isServerPagination) {
				setTotalCount(data.length);
			}
		}, [data, isServerPagination]);

		const handleSnoozeItem = (weeks: number): ((item: JamData) => Promise<void>) => {
			return async (item: JamData): Promise<void> => {
				try {
					const snoozeDate = new Date();
					snoozeDate.setDate(snoozeDate.getDate() + weeks * 7);
					const response: ApiResponse<JamData> = await dataContext.updateEntity(entityType, item.id, {
						followup_snooze_datetime: snoozeDate.toISOString(),
					});
					if ("title" in response.data) {
						showToastSuccess(
							`${response.data.title} was snoozed for ${weeks} week` + (weeks > 1 ? "s" : "") + "."
						);
					}
				} catch (error) {
					showToastError(`Failed to snooze ${(item as EnrichedJobData).title}. Please try again.`);
				}
			};
		};

		// Get context menu items based on mode
		const getContextMenuItems = (item: JamData): MenuItem[] => {
			let baseItems: MenuItem[] = [
				{
					action: "view",
					icon: "eye",
					text: "View",
					function: openViewModal,
				},
				{
					action: "edit",
					icon: "pencil",
					text: "Edit",
					function: openEditModal,
				},
				{
					action: "snooze",
					icon: "alarm",
					text: "Snooze for...",
					submenus: [
						{
							action: "snooze-1",
							text: "1 week",
							function: handleSnoozeItem(1),
							showLoading: true,
							loadingMessage: "Snoozing Job...",
						},
						{
							action: "snooze-2",
							text: "2 weeks",
							function: handleSnoozeItem(2),
							showLoading: true,
							loadingMessage: "Snoozing Job...",
						},
						{
							action: "snooze-3",
							text: "3 weeks",
							function: handleSnoozeItem(3),
							showLoading: true,
							loadingMessage: "Snoozing Job...",
						},
						{
							action: "snooze-4",
							text: "4 weeks",
							function: handleSnoozeItem(4),
							showLoading: true,
							loadingMessage: "Snoozing Job...",
						},
					],
				},
				{
					action: "import",
					icon: "upload",
					text: "Import",
					function: openImportModal,
				},
				{
					action: "delete",
					icon: "trash",
					text: "Delete",
					color: "#dc3545",
					function: handleDelete,
				},
				{
					action: "activate",
					icon: "check-circle",
					text: "Activate",
					function: activateEntityHandler,
					showLoading: true,
					loadingMessage: "Activating Scraping Filter...",
				},
				{
					action: "deactivate",
					icon: "slash-circle",
					text: "Deactivate",
					function: deactivateEntityHandler,
					showLoading: true,
					loadingMessage: "Deactivating Scraping Filter...",
				},
				{
					action: "followup",
					icon: "bell",
					text: "Follow-up Email",
					function: (item: JamData): void => {
						followUpModalRef.current?.show(item as JobData);
					},
				},
			];

			let allowedActions: string[];

			if (typeof menuItems === "function") {
				allowedActions = menuItems(item);
			} else if (menuItems) {
				allowedActions = menuItems;
			} else {
				if (mode === "import") {
					allowedActions = ["import", "delete"];
				} else {
					allowedActions = ["view", "edit", "delete"];
				}
			}
			return allowedActions
				.map((action: string): MenuItem | undefined =>
					baseItems.find((menuItem: MenuItem): boolean => menuItem.action === action)
				)
				.filter((item: MenuItem | undefined): item is MenuItem => item !== undefined);
		};

		const handleRowRightClick = (item: any, event: MouseEvent<HTMLTableRowElement>): void => {
			event.preventDefault();
			event.stopPropagation();

			const items: MenuItem[] = getContextMenuItems(item);
			openContextMenu(
				event as any, // Cast to satisfy MouseEvent<HTMLElement>
				items,
				item,
				compact
			);
		};
		// Get button text based on mode
		const getAddButtonText = (): string => {
			if (mode === "import") {
				return `Import ${entityName}`;
			} else {
				return `Add ${entityName}`;
			}
		};

		// Get button icon based on mode
		const getAddButtonIcon = () => {
			if (mode === "import") {
				return "bi-upload";
			}
			return "bi-plus-circle";
		};
		// Render
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
			<>
				<div className={"table-container"}>
					{title && (
						<PageHeader
							title={title}
							count={totalFilteredCount || data.length}
							icon={getTableIcon(title)}
						/>
					)}

					<div
						className={`d-flex justify-content-between ${compact ? "mb-2" : "mb-3"}`}
						style={{ gap: compact ? "0.5rem" : "1rem" }}
					>
						{showSearch && !compact && (
							<div className="d-flex align-items-center gap-3" style={{ flex: 1, width: "auto" }}>
								<input
									type="text"
									className="form-control"
									placeholder="Search..."
									value={searchTerm}
									onChange={(e): void => setSearchTerm(e.target.value)}
									id="search-input"
								/>
								<span className="text-muted small" style={{ whiteSpace: "nowrap" }}>
									Showing {totalFilteredCount} of {totalCount} Entries
								</span>
							</div>
						)}
						{toolbarAddon && <div className="datatable-toolbar-addon">{toolbarAddon}</div>}
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
								id={`add-${entityType}-button`}
							>
								<i className={`${getAddButtonIcon()} me-2`} style={{ fontSize: "1.1rem" }}></i>
								{getAddButtonText()}
							</Button>
						)}
					</div>

					{/* Table */}
					{showSpinner ? (
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
											{columns.map(
												(column: TableColumn): JSX.Element => (
													<th key={column.key} style={compact ? { padding: "0.5rem" } : {}}>
														<div className="d-flex align-items-center justify-content-between">
															<div
																className={
																	column.sortable
																		? "cursor-pointer user-select-none"
																		: ""
																}
																onClick={() =>
																	column.sortable && handleSort(column.key)
																}
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
																			style={
																				compact
																					? {
																							fontSize: "0.75rem",
																						}
																					: {}
																			}
																		></i>
																	</span>
																)}
															</div>
														</div>
													</th>
												)
											)}
										</tr>
									</thead>
									<tbody>
										{currentPageData.map(
											(item: JamData, index: number): JSX.Element => (
												<tr
													key={item.id || index}
													id={`table-row-${entityType}-${item.id}`}
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
											)
										)}
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
													{emptyMessage || `No ${pluralize(entityName)} found`}
												</td>
											</tr>
										)}
									</tbody>
								</table>
							</div>

							{/* Pagination */}
							{!showAllEntries && totalFilteredCount > 20 && (
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
										].map(
											({ action, disabled, icon, label }): JSX.Element => (
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
											)
										)}
									</div>
									<div className="d-flex align-items-center gap-2">
										<span
											className={`small text-muted text-nowrap`}
											style={compact ? { fontSize: "0.75rem" } : {}}
										>
											{currentPage * pageSize + 1} to{" "}
											{Math.min((currentPage + 1) * pageSize, totalFilteredCount)} of{" "}
											{totalFilteredCount}
										</span>

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
											onChange={(e): void => {
												setPageSize(Number(e.target.value));
											}}
										>
											{[20, 30, 40, 50, 100].map(
												(size): JSX.Element => (
													<option key={size} value={size}>
														Show {size} Entries
													</option>
												)
											)}
										</Form.Select>
									</div>
								</div>
							)}
						</>
					)}

					{children ? children(data) : null}
					<Modal
						ref={modalRef}
						onSuccess={handleSuccess}
						onDelete={handleDeleteSuccess}
						size={modalSize}
						{...modalProps}
					/>
				</div>
				<FollowUpModal ref={followUpModalRef} />
			</>
		);
	}
);

DataTable.displayName = "DataTable";

export default DataTable;
