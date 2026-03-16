import React, {
	forwardRef,
	JSX,
	MouseEvent,
	ReactNode,
	useCallback,
	useEffect,
	useImperativeHandle,
	useMemo,
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
import PageHeader, { FilterPill } from "../../pages/PageHeader/PageHeader";
import { ColumnConfig, useColumnConfig } from "../../hooks/useColumnConfig";
import ColumnConfigSidebar from "./ColumnConfigSidebar";
import FilterSidebar from "./FilterSidebar";
import {
	ActiveFilters,
	countActiveFilters,
	DatePreset,
	isFilterActive,
	ReferenceFilterConfig,
	SelectFilterConfig,
} from "./FilterTypes";
import { applyFilters } from "./filterLogic";
import BulkActionsDropdown from "./BulkActionsDropdown";

export type BulkAction =
	| {
			type?: "action";
			label: string;
			icon?: string;
			variant?: string;
			onClick: (ids: string[]) => void | Promise<void>;
	  }
	| { type: "divider" }
	| { type: "header"; label: string };

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

	// Column configuration
	enableColumnConfig?: boolean;

	// Multi-select
	enableMultiSelect?: boolean;
	bulkActions?: BulkAction[];
	rowIndicator?: (item: JamData) => boolean;
}

export interface DataTableHandle {
	openAddModal: (data?: any) => void;
	clearSelection: () => void;
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
			toolbarAddon,
			reloadTrigger,
			queryParams,
			defaultModalMode = "view",
			enableColumnConfig = false,
			enableMultiSelect = false,
			bulkActions = [],
			rowIndicator,
		}: GenericTableProps,
		ref
	): JSX.Element => {
		const { token } = useAuth();
		const columnConfig: ColumnConfig = useColumnConfig(entityType, enableColumnConfig ? columns : undefined);
		const [columnSidebarOpen, setColumnSidebarOpen] = useState<boolean>(false);
		const [filterSidebarOpen, setFilterSidebarOpen] = useState<boolean>(false);
		const [filters, setFilters] = useState<ActiveFilters>({});
		const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set());
		const effectiveColumns: TableColumn[] = enableColumnConfig ? columnConfig.visibleColumns : columns;
		const columnSidebarRef = useRef<HTMLDivElement>(null);
		const filterSidebarRef = useRef<HTMLDivElement>(null);
		const modalRef = useRef<DataModalHandle>(null);
		const openViewModal = (item: any): void | undefined => modalRef.current?.showView(item);
		const openEditModal = (item: any): void | undefined => modalRef.current?.showEdit(item);
		const openAddModal = (data?: any) => modalRef.current?.showAdd(data ?? initialData);
		const openImportModal = (item: any): void | undefined => modalRef.current?.showImport(item);

		useImperativeHandle(ref, () => ({ openAddModal, clearSelection: () => setSelectedIds(new Set()) }));

		// Close sidebars on outside click
		useEffect(() => {
			if (!columnSidebarOpen && !filterSidebarOpen) return;
			const handleClickOutside = (e: Event) => {
				const target = e.target as Element;
				// Ignore clicks on portalled menus (react-select dropdowns)
				if (target?.closest?.(".react-select__menu-portal")) return;
				// Ignore clicks on sidebar toggle buttons
				if (target?.closest?.("[data-sidebar-toggle]")) return;
				const isInsideAnySidebar =
					columnSidebarRef.current?.contains(target) || filterSidebarRef.current?.contains(target);
				if (!isInsideAnySidebar) {
					if (columnSidebarOpen) setColumnSidebarOpen(false);
					if (filterSidebarOpen) setFilterSidebarOpen(false);
				}
			};
			document.addEventListener("mousedown", handleClickOutside);
			return () => document.removeEventListener("mousedown", handleClickOutside);
		}, [columnSidebarOpen, filterSidebarOpen]);

		// Add context menu hook
		const { openContextMenu } = useContextMenu();

		// Data management
		const dataContext: DataContextValue = useDataContext();
		const filterPills: FilterPill[] = useMemo(() => {
			return Object.entries(filters)
				.filter(([, val]) => isFilterActive(val))
				.flatMap(([key, val]) => {
					const allCols = enableColumnConfig ? columnConfig.allColumns : effectiveColumns;
					const col = allCols.find((c) => c.key === key);
					if (!col) return [];
					let summary = "";
					switch (val.type) {
						case "text":
							summary = `"${val.value}"`;
							break;
						case "select": {
							const cfg = col.filterConfig as SelectFilterConfig;
							const names = val.selected.map((v) => cfg.options.find((o) => o.value === v)?.label ?? v);
							summary = names.slice(0, 2).join(", ");
							if (names.length > 2) summary += ` +${names.length - 2}`;
							break;
						}
						case "date": {
							if (val.preset === "custom" && !val.from && !val.to) return [];
							const presetLabels: Record<DatePreset, string> = {
								last7: "Last 7 days",
								last30: "Last 30 days",
								next7: "Next 7 days",
								next30: "Next 30 days",
								thisMonth: "This month",
								pastDeadline: "Past deadline",
								custom: "",
							};
							if (val.preset && val.preset !== "custom") {
								summary = presetLabels[val.preset];
							} else if (val.from && val.to) {
								summary = `${val.from} \u2013 ${val.to}`;
							} else if (val.from) {
								summary = `From ${val.from}`;
							} else {
								summary = `Until ${val.to}`;
							}
							break;
						}
						case "number": {
							const parts: string[] = [];
							if (val.min !== null && val.max !== null) parts.push(`${val.min} \u2013 ${val.max}`);
							else if (val.min !== null) parts.push(`\u2265 ${val.min}`);
							else if (val.max !== null) parts.push(`\u2264 ${val.max}`);
							if (val.nullFilter === "not_null") parts.push("Not null");
							else if (val.nullFilter === "null") parts.push("Null only");
							summary = parts.join(", ");
							break;
						}
						case "reference": {
							const cfg = col.filterConfig as ReferenceFilterConfig;
							const entities: any[] = (dataContext as any)[cfg.entityKey] ?? [];
							const lk = cfg.labelKey ?? "name";
							const names = val.selectedIds.map((id) => {
								const e = entities.find((en) => String(en.id) === id);
								return e ? String(e[lk] ?? e.id) : id;
							});
							summary = names.slice(0, 2).join(", ");
							if (names.length > 2) summary += ` +${names.length - 2}`;
							break;
						}
					}
					return [
						{
							key,
							label: col.label,
							summary,
							onRemove: () =>
								setFilters((prev) => {
									const u = { ...prev };
									delete u[key];
									return u;
								}),
						},
					];
				});
		}, [filters, effectiveColumns, dataContext, enableColumnConfig, columnConfig.allColumns]);
		const [isLoading, setIsLoading] = useState<boolean>(false);
		const [loadError, setLoadError] = useState<string | null>(null);
		const [fetchedData, setFetchedData] = useState<any[]>([]);
		const [debouncedSearchTerm, setDebouncedSearchTerm] = useState<string>("");

		// Search and sort — saved sort preference takes priority over prop default
		const effectiveInitialSort: SortConfig = (enableColumnConfig && columnConfig.savedSort) ||
			(initialSortConfig as SortConfig) || { key: "created_at", direction: "desc" };
		const [sortConfig, setSortConfig] = useState<SortConfig>(effectiveInitialSort);
		const prevSavedSortRef = useRef(columnConfig.savedSort);

		// Sync sortConfig when saved sort changes externally (e.g. from sidebar)
		useEffect(() => {
			const prev = prevSavedSortRef.current;
			const next = columnConfig.savedSort;
			if (enableColumnConfig && next && (prev?.key !== next.key || prev?.direction !== next.direction)) {
				setSortConfig(next);
			}
			prevSavedSortRef.current = next;
		}, [columnConfig.savedSort, enableColumnConfig]);

		const [searchTerm, setSearchTerm] = useState<string>("");

		// UI state
		const { showToastSuccess, showToastError } = useGlobalToast();
		const [currentPage, setCurrentPage] = useState<number>(0);
		const [pageSize, setPageSize] = useState<number>(20);
		const [totalCount, setTotalCount] = useState<number>(0);
		const [showSpinner, setShowSpinner] = useState<boolean>(false);
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

		// Reset page when debounced search or filters change
		useEffect(() => {
			setCurrentPage(0);
			setSelectedIds(new Set());
		}, [debouncedSearchTerm, sortConfig, pageSize, filters]);

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

				// Send active column filters to the backend
				const activeFilterEntries = Object.entries(filters).filter(([, v]) => isFilterActive(v));
				if (activeFilterEntries.length > 0) {
					params.set("filters", JSON.stringify(Object.fromEntries(activeFilterEntries)));
				}

				const response: ApiResponse = await baseApi.get(`${endpoint}/paged?${params.toString()}`, token);
				setFetchedData(response.data.items);
				setTotalCount(response.data.total);
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
		}, [
			endpoint,
			token,
			currentPage,
			pageSize,
			sortConfig,
			isServerPagination,
			debouncedSearchTerm,
			queryParams,
			filters,
		]);

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
			if (searchTermLower && effectiveColumns.some((col: TableColumn): boolean | undefined => col.searchable)) {
				filteredData = filteredData.filter((item: JamData): boolean => {
					return effectiveColumns.some((column: TableColumn): boolean | undefined => {
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

			// Apply column filters
			if (Object.keys(filters).length > 0) {
				filteredData = applyFilters(
					filteredData,
					filters,
					enableColumnConfig ? columnConfig.allColumns : effectiveColumns,
					dataContext
				);
			}

			// Sort data
			if (sortConfig.key) {
				filteredData.sort((a: any, b: any): 0 | 1 | -1 => {
					const column: TableColumn | undefined = effectiveColumns.find(
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

			if (mode === "import") {
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
		};

		const handleDeleteSuccess = (): void => {
			if (isServerPagination) {
				fetchData().then((): null => null);
			}
		};

		// Pagination calculations
		const sortedData: JamData[] = isServerPagination ? data : getSortedData();
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
				const startIndex: number = currentPage * pageSize;
				const endIndex: number = startIndex + pageSize;
				currentPageData = sortedData.slice(startIndex, endIndex);
			}
		}

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

		// Bulk selection handlers
		const handleSelectAll = (checked: boolean): void => {
			if (checked) {
				setSelectedIds(new Set(currentPageData.map((item: any) => item.id)));
			} else {
				setSelectedIds(new Set());
			}
		};

		const handleSelectRow = (id: string | number, checked: boolean): void => {
			setSelectedIds((prev) => {
				const next = new Set(prev);
				if (checked) next.add(id);
				else next.delete(id);
				return next;
			});
		};

		const handleBulkAction = async (action: Extract<BulkAction, { type?: "action" }>): Promise<void> => {
			let ids: string[];
			if (selectedIds.size > 0) {
				ids = [...selectedIds].map(String);
			} else if (isServerPagination && totalCount > 0) {
				try {
					const params = new URLSearchParams({
						page: "0",
						page_size: totalCount.toString(),
						sort_by: sortConfig.key,
						sort_direction: sortConfig.direction,
						search: debouncedSearchTerm,
					});
					if (queryParams) {
						Object.entries(queryParams).forEach(([key, value]) => params.set(key, value));
					}
					const activeFilterEntries = Object.entries(filters).filter(([, v]) => isFilterActive(v));
					if (activeFilterEntries.length > 0) {
						params.set("filters", JSON.stringify(Object.fromEntries(activeFilterEntries)));
					}
					const response: ApiResponse = await baseApi.get(`${endpoint}/paged?${params.toString()}`, token);
					ids = response.data.items.map((item: any) => String(item.id));
				} catch {
					ids = currentPageData.map((item: any) => String(item.id));
				}
			} else {
				ids = sortedData.map((item: any) => String(item.id));
			}
			await action.onClick(ids);
			setSelectedIds(new Set());
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
				<div className={`table-container${!compact ? " table-container--full-height" : ""}`}>
					{title && (
						<PageHeader
							title={title}
							count={totalCount || data.length}
							icon={getTableIcon(title)}
							filterPills={filterPills}
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
									Showing {displayTotal} Entries
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
								<i className={`bi-plus-circle me-2`} style={{ fontSize: "1.1rem" }}></i>
								{`Add ${entityName}`}
							</Button>
						)}
						{enableMultiSelect && (
							<BulkActionsDropdown
								selectedCount={selectedIds.size}
								totalCount={displayTotal}
								actions={bulkActions}
								onAction={handleBulkAction}
								onClearSelection={() => setSelectedIds(new Set())}
							/>
						)}
						{enableColumnConfig && !compact && (
							<Button
								id="column-config-toggle-btn"
								variant={columnSidebarOpen ? "primary" : "outline-primary"}
								onClick={() => {
									setColumnSidebarOpen(!columnSidebarOpen);
									setFilterSidebarOpen(false);
								}}
								className={"config-btn"}
								data-sidebar-toggle="column"
							>
								<i className="bi bi-gear"></i>
							</Button>
						)}
						{enableColumnConfig && !compact && (
							<Button
								id="filter-toggle-btn"
								variant={filterSidebarOpen ? "primary" : "outline-primary"}
								className={"config-btn"}
								onClick={() => {
									setFilterSidebarOpen(!filterSidebarOpen);
									setColumnSidebarOpen(false);
								}}
								data-sidebar-toggle="filter"
							>
								<i className="bi bi-funnel"></i>
								{countActiveFilters(filters) > 0 && (
									<span
										className="filter-button-count"
										style={{
											position: "absolute",
											top: "-6px",
											left: "-6px",
											fontSize: "0.65rem",
										}}
									>
										{countActiveFilters(filters)}
									</span>
								)}
							</Button>
						)}
					</div>

					{/* Table */}
					{showSpinner ? (
						<LoadingSpinner text="Loading..." />
					) : (
						<>
							<div style={{ display: "flex", minHeight: 0, flex: 1 }}>
								<div className="table-responsive" style={{ minWidth: 0, width: "100%" }}>
									<table
										className={`table table-striped table-hover ${compact ? "table-sm rounded-3 overflow-hidden" : ""}`}
										style={{
											...(compact ? { fontSize: "0.875rem" } : {}),
											...(!compact
												? {
														gridTemplateColumns: [
															...(enableMultiSelect ? ["2rem"] : []),
															...effectiveColumns.map((col, i) => {
																const min = col.minWidth ?? "auto";
																return i === 0
																	? `minmax(${min}, 1fr)`
																	: `minmax(${min}, auto)`;
															}),
														].join(" "),
													}
												: {}),
										}}
									>
										<thead className="custom-header">
											<tr>
												{enableMultiSelect && (
													<th
														style={{
															width: "2rem",
															...(compact ? { padding: "0.5rem" } : {}),
														}}
													>
														<input
															type="checkbox"
															className="form-check-input"
															ref={(el) => {
																if (el) {
																	const allSel =
																		currentPageData.length > 0 &&
																		currentPageData.every((i: any) =>
																			selectedIds.has(i.id)
																		);
																	const someSel = currentPageData.some((i: any) =>
																		selectedIds.has(i.id)
																	);
																	el.indeterminate = someSel && !allSel;
																	el.checked = allSel;
																}
															}}
															onChange={(e) => handleSelectAll(e.target.checked)}
														/>
													</th>
												)}
												{effectiveColumns.map(
													(column: TableColumn): JSX.Element => (
														<th
															key={column.key}
															style={compact ? { padding: "0.5rem" } : {}}
														>
															<div
																className="d-flex align-items-center justify-content-between"
																style={{ whiteSpace: "nowrap" }}
															>
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
														className={`table-row-clickable${rowIndicator && rowIndicator(item) ? " table-row--new" : ""}`}
														onClick={(e) => handleRowClick(e, item)}
														onContextMenu={(e) => handleRowRightClick(item, e)}
														style={{ cursor: "pointer" }}
													>
														{enableMultiSelect && (
															<td
																style={{
																	width: "2rem",
																	...(compact
																		? { padding: "0.5rem", fontSize: "0.875rem" }
																		: {}),
																}}
																onClick={(e) => e.stopPropagation()}
															>
																<input
																	type="checkbox"
																	className="form-check-input"
																	checked={selectedIds.has(item.id)}
																	onChange={(e) =>
																		handleSelectRow(item.id, e.target.checked)
																	}
																/>
															</td>
														)}
														{effectiveColumns.map((column, columnIndex) => (
															<td
																key={column.key}
																className={`align-middle${columnIndex === 0 && rowIndicator && rowIndicator(item) ? " table-cell--new" : ""}`}
																style={{
																	...(columnIndex === 0
																		? { fontWeight: "bold" }
																		: {}),
																	...(compact
																		? {
																				padding: "0.5rem",
																				fontSize: "0.875rem",
																			}
																		: {}),
																}}
															>
																{columnIndex === 0 &&
																	rowIndicator &&
																	rowIndicator(item) && (
																		<span
																			className="badge rounded-pill bg-primary me-2"
																			style={{ fontSize: "0.6rem" }}
																		>
																			NEW
																		</span>
																	)}
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
														colSpan={effectiveColumns.length + (enableMultiSelect ? 1 : 0)}
														className="text-center py-4 text-muted"
														style={{
															gridColumn: "1 / -1",
															justifyContent: "center",
															...(compact
																? { padding: "1rem", fontSize: "0.875rem" }
																: {}),
														}}
													>
														{emptyMessage || `No ${pluralize(entityName)} found`}
													</td>
												</tr>
											)}
										</tbody>
									</table>
								</div>
								{enableColumnConfig && (
									<div ref={columnSidebarRef}>
										<ColumnConfigSidebar
											isOpen={columnSidebarOpen}
											onClose={() => setColumnSidebarOpen(false)}
											allColumns={columnConfig.allColumns}
											columnOrder={columnConfig.columnOrder}
											isDefault={columnConfig.isDefault}
											onSave={columnConfig.setColumnConfig}
											onReset={columnConfig.resetToDefaults}
											currentSort={sortConfig}
											onSortChange={columnConfig.setSortConfig}
										/>
									</div>
								)}
								{enableColumnConfig && (
									<div ref={filterSidebarRef}>
										<FilterSidebar
											isOpen={filterSidebarOpen}
											onClose={() => setFilterSidebarOpen(false)}
											columns={columnConfig.allColumns}
											filters={filters}
											onFiltersChange={setFilters}
										/>
									</div>
								)}
							</div>

							{/* Pagination */}
							{!showAllEntries && displayTotal > 20 && (
								<div className={`d-flex justify-content-between align-items-center mt-1`}>
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
