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
import { Button } from "react-bootstrap";
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
import FilterPillsRow from "./FilterPillsRow";
import { ColumnConfig, useColumnConfig } from "../../hooks/useColumnConfig";
import ColumnConfigSidebar from "./ColumnConfigSidebar";
import FilterSidebar from "./FilterSidebar";
import ClearButton from "./ClearButton";
import { CustomSelect } from "../rendering/widgets/CustomSelect";
import { SelectOption } from "../rendering/form/FormOptions";
import { isFilterActive } from "./FilterTypes";
import { applyFilters } from "./filterLogic";
import BulkActionsDropdown from "./BulkActionsDropdown";
import { useTableFilters } from "./useTableFilters";
import { Direction, SortConfig } from "../../services/schemas/Core";

export type BulkAction =
	| {
			type?: "action";
			label: string;
			icon?: string;
			variant?: string;
			onClick: (ids: number[]) => void | Promise<void>;
	  }
	| { type: "divider" }
	| { type: "header"; label: string };

export interface DataTableProps {
	data?: any | null;
	columns?: TableColumn[];
	showAdd?: boolean;
	menuItems?: string[] | ((item: JamData) => string[]);
	title?: string;
	onTotalCountChange?: (count: number) => void;
	onSuccess?: () => void;
	reloadTrigger?: number;
	modalProps?: any;
}

export interface GenericTableProps<T extends JamData = JamData> {
	// Data source - entity type from DataContext
	entityType: EntityType;
	data?: T[];

	// Mode
	mode?: "default" | "import";

	// Optional endpoint when data are not provided or not fetched from context
	endpoint?: string;

	// Table configuration
	columns?: TableColumn[];
	initialSortConfig?: Partial<SortConfig>;
	menuItems?: string[] | ((item: T) => string[]);
	rowMode?: (item: T) => "default" | "import";

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
	children?: (data: T[]) => ReactNode;
	toolbarAddon?: React.ReactNode;
	reloadTrigger?: number;
	queryParams?: Record<string, string>;

	// Column configuration
	enableColumnConfig?: boolean;

	// Multi-select
	enableMultiSelect?: boolean;
	bulkActions?: BulkAction[];
	rowIndicator?: (item: T) => boolean;
	rowReadIndicator?: (item: T) => boolean;

	smallSearch?: boolean;
	onTotalCountChange?: (count: number) => void;
	onSuccess?: () => void;
	onItemOpen?: (item: T) => void;
}

export interface DataTableHandle {
	openAddModal: (data?: any) => void;
	clearSelection: () => void;
}

function DataTableComponent<T extends JamData>(
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
		enableColumnConfig = false,
		enableMultiSelect = false,
		bulkActions = [],
		rowIndicator,
		rowReadIndicator,
		smallSearch = false,
		onTotalCountChange,
		onSuccess,
		onItemOpen,
	}: GenericTableProps<T>,
	ref: React.Ref<DataTableHandle>
): JSX.Element {
	const { token } = useAuth();
	const columnConfig: ColumnConfig = useColumnConfig(entityType, enableColumnConfig ? columns : undefined);
	const [columnSidebarOpen, setColumnSidebarOpen] = useState<boolean>(false);
	const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
	const effectiveColumns: TableColumn[] = enableColumnConfig ? columnConfig.visibleColumns : columns;
	const columnSidebarRef = useRef<HTMLDivElement>(null);
	const dataContext: DataContextValue = useDataContext();
	const {
		filters,
		setFilters,
		filterSidebarOpen,
		setFilterSidebarOpen,
		filterSidebarRef,
		filterPills,
		activeFilterCount,
	} = useTableFilters({ enableColumnConfig, columnConfig, effectiveColumns, dataContext });
	const modalRef = useRef<DataModalHandle<T>>(null);
	const openViewModal = (item: T): void | undefined => modalRef.current?.showView(item);
	const openEditModal = (item: T): void | undefined => modalRef.current?.showEdit(item);
	const openAddModal = (data?: any) => modalRef.current?.showAdd(data ?? initialData);
	const openImportModal = (item: T): void | undefined => modalRef.current?.showImport(item);

	useImperativeHandle(ref, () => ({ openAddModal, clearSelection: () => setSelectedIds(new Set()) }));

	// Close sidebars on outside click
	useEffect(() => {
		if (!columnSidebarOpen && !filterSidebarOpen) return;
		const handleClickOutside = (e: Event) => {
			const target = e.target as Element;
			// Ignore clicks on portalled menus (custom select dropdowns)
			if (target?.closest?.(".jam-select__portal")) return;
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

	const [isLoading, setIsLoading] = useState<boolean>(false);
	const [loadError, setLoadError] = useState<string | null>(null);
	const [fetchedData, setFetchedData] = useState<T[]>([]);
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

	// Reset page when debounced search or filters change
	useEffect(() => {
		setCurrentPage(0);
		setSelectedIds(new Set());
	}, [debouncedSearchTerm, sortConfig, pageSize, filters]);

	const buildPagedParams = (page: number, size: number): URLSearchParams => {
		const params = new URLSearchParams({
			page: page.toString(),
			page_size: size.toString(),
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
		return params;
	};

	const fetchData = async (): Promise<void> => {
		setIsLoading(true);
		setLoadError(null);
		try {
			const params: URLSearchParams = buildPagedParams(currentPage, pageSize);
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

	const getData = (): T[] => {
		if (providedData !== undefined) {
			return providedData;
		}
		if (isServerPagination) {
			return fetchedData;
		}
		return dataContext.getEntityData(entityType) as T[];
	};

	const data: T[] = getData();
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
	const getSortedData = (): T[] => {
		let filteredData: T[] = [...data];
		const searchTermLower: string = searchTerm.toLowerCase();

		// Filter by search term
		if (searchTermLower && effectiveColumns.some((col: TableColumn): boolean | undefined => col.searchable)) {
			filteredData = filteredData.filter((item: T): boolean => {
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
						value = (item as any)[column.key];
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
			) as T[];
		}

		// Sort data
		if (sortConfig.key) {
			filteredData.sort((a: T, b: T): 0 | 1 | -1 => {
				const column: TableColumn | undefined = effectiveColumns.find(
					(col: TableColumn): boolean => col.key === sortConfig.key
				);
				let aValue: any, bValue: any;
				if (!column) return 0;

				if (typeof column.sortField === "function") {
					aValue = column.sortField(a, dataContext);
					bValue = column.sortField(b, dataContext);
				} else if (typeof column.sortField === "string") {
					aValue = (a as any)[column.sortField];
					bValue = (b as any)[column.sortField];
				} else {
					aValue = (a as any)[column.key];
					bValue = (b as any)[column.key];
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
	const handleRowClick = (event: MouseEvent<HTMLTableRowElement>, item: T): void => {
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

		onItemOpen?.(item);
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

	const handleDelete = async (item: T): Promise<boolean> => {
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
	const sortedData: T[] = isServerPagination ? data : getSortedData();
	let currentPageData: T[];
	let totalPages: number;
	const displayTotal: number = isServerPagination ? totalFilteredCount : sortedData.length;

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

	const handleSnoozeItem = (weeks: number): ((item: T) => Promise<void>) => {
		return async (item: T): Promise<void> => {
			try {
				const snoozeDate = new Date();
				snoozeDate.setDate(snoozeDate.getDate() + weeks * 7);
				const response: ApiResponse<JamData> = await dataContext.updateEntity(entityType, item.id, {
					followup_snooze_datetime: snoozeDate,
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
	const getContextMenuItems = (item: T): MenuItem[] => {
		let baseItems: MenuItem[] = [
			{
				action: "view",
				icon: "eye",
				text: "View",
				function: openViewModal as (item: JamData) => void,
			},
			{
				action: "edit",
				icon: "pencil",
				text: "Edit",
				function: openEditModal as (item: JamData) => void,
			},
			{
				action: "snooze",
				icon: "alarm",
				text: "Snooze for...",
				submenus: [
					{
						action: "snooze-1",
						text: "1 week",
						function: handleSnoozeItem(1) as (item: JamData) => Promise<void>,
						showLoading: true,
						loadingMessage: "Snoozing Job...",
					},
					{
						action: "snooze-2",
						text: "2 weeks",
						function: handleSnoozeItem(2) as (item: JamData) => Promise<void>,
						showLoading: true,
						loadingMessage: "Snoozing Job...",
					},
					{
						action: "snooze-3",
						text: "3 weeks",
						function: handleSnoozeItem(3) as (item: JamData) => Promise<void>,
						showLoading: true,
						loadingMessage: "Snoozing Job...",
					},
					{
						action: "snooze-4",
						text: "4 weeks",
						function: handleSnoozeItem(4) as (item: JamData) => Promise<void>,
						showLoading: true,
						loadingMessage: "Snoozing Job...",
					},
				],
			},
			{
				action: "import",
				icon: "upload",
				text: "Import",
				function: openImportModal as (item: JamData) => void,
			},
			{
				action: "delete",
				icon: "trash",
				text: "Delete",
				color: "#dc3545",
				function: handleDelete as (item: JamData) => Promise<boolean>,
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

	const handleRowRightClick = (item: T, event: MouseEvent<HTMLTableRowElement>): void => {
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
			setSelectedIds(new Set(currentPageData.map((item: T) => item.id)));
		} else {
			setSelectedIds(new Set());
		}
	};

	const handleSelectRow = (id: number, checked: boolean): void => {
		setSelectedIds((prev) => {
			const next = new Set(prev);
			if (checked) next.add(id);
			else next.delete(id);
			return next;
		});
	};

	const handleBulkAction = async (action: Extract<BulkAction, { type?: "action" }>): Promise<void> => {
		try {
			let ids: number[];
			if (selectedIds.size > 0) {
				ids = [...selectedIds];
			} else if (isServerPagination && totalCount > 0) {
				const params: URLSearchParams = buildPagedParams(0, totalCount);
				params.set("ids_only", "true");
				const response: ApiResponse = await baseApi.get(`${endpoint}/paged?${params.toString()}`, token);
				ids = response.data.items.map(String);
			} else {
				ids = sortedData.map((item: T): number => item.id);
			}
			await action.onClick(ids);
			setSelectedIds(new Set());
		} catch (error: any) {
			showToastError(error?.message || "Bulk action failed. Please try again.");
		}
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
			{title && <PageHeader title={title} count={totalFilteredCount || data.length} icon={getTableIcon(title)} />}

			<div className={`table-container${!compact ? " table-container--full-height" : ""}`}>
				<div
					className={`datatable-toolbar ${compact ? "mb-2" : "mb-3"}${compact ? " datatable-toolbar--compact" : ""}`}
				>
					{showSearch && !compact && (
						<div className="datatable-toolbar-search">
							<div className="search-input-wrapper">
								<input
									type="text"
									className="form-control"
									style={smallSearch ? { height: "35px", minHeight: "unset" } : {}}
									placeholder="Search..."
									value={searchTerm}
									onChange={(e): void => setSearchTerm(e.target.value)}
									id="search-input"
								/>
								{searchTerm && (
									<ClearButton onClick={() => setSearchTerm("")} ariaLabel="Clear search" size="md" />
								)}
							</div>
							<span className="datatable-toolbar-count text-muted small">
								Showing {totalFilteredCount} of {totalCount} Entries
							</span>
						</div>
					)}
					<div className="datatable-toolbar-actions" style={!compact && showAdd && mode !== "import" ? { flex: 1 } : undefined}>
						{toolbarAddon && <div className="datatable-toolbar-addon">{toolbarAddon}</div>}
						{showAdd && mode !== "import" && (
							<Button
								variant="primary"
								{...(compact ? { size: "sm" as const } : {})}
								onClick={() => openAddModal()}
								className="d-flex align-items-center justify-content-center"
								style={{
									flex: compact ? undefined : 1,
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
								{activeFilterCount > 0 && (
									<span
										className="filter-button-count"
										style={{
											position: "absolute",
											top: "-6px",
											left: "-6px",
											fontSize: "0.65rem",
										}}
									>
										{activeFilterCount}
									</span>
								)}
							</Button>
						)}
					</div>
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
																	currentPageData.every((i: T) =>
																		selectedIds.has(i.id)
																	);
																const someSel = currentPageData.some((i: T) =>
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
													<th key={column.key} style={compact ? { padding: "0.5rem" } : {}}>
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
										<FilterPillsRow
											filterPills={filterPills}
											onClear={(): void => setFilters({})}
										/>
										{currentPageData.map(
											(item: T, index: number): JSX.Element => (
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
													{effectiveColumns.map(
														(column: TableColumn, columnIndex: number): JSX.Element => (
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
																{columnIndex === 0 &&
																	rowReadIndicator &&
																	rowReadIndicator(item) && (
																		<span className="read-dot me-2" />
																	)}
																<RenderViewFieldWithContext
																	field={column}
																	item={item}
																	id={`table-row-${item.id}`}
																/>
															</td>
														)
													)}
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
														...(compact ? { padding: "1rem", fontSize: "0.875rem" } : {}),
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
									<CustomSelect
										id="page-items-select"
										options={[20, 30, 40, 50, 100].map(
											(s: number): SelectOption => ({
												value: String(s),
												label: `Show ${s} Entries`,
											})
										)}
										value={{ value: String(pageSize), label: `Show ${pageSize} Entries` }}
										onChange={(opt): void => {
											if (opt && !Array.isArray(opt))
												setPageSize(Number((opt as SelectOption).value));
										}}
										isSearchable={false}
										isClearable={false}
										size="sm"
									/>
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

export const DataTable = forwardRef(DataTableComponent) as (<T extends JamData>(
	props: GenericTableProps<T> & { ref?: React.Ref<DataTableHandle> }
) => JSX.Element) & { displayName?: string };

DataTable.displayName = "DataTable";

export default DataTable;
