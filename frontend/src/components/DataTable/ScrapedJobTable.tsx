import React, { JSX, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Button } from "react-bootstrap";
import { DataTable, DataTableHandle, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../DataModal/ScrapedJobModal";
import { ScrapedJobData, ScrapingFilterData } from "../../services/schemas/Services";
import { DataContextValue, JamData, useDataContext } from "../../contexts/DataContext";
import { useAuth } from "../../contexts/AuthContext";
import { ActionToggle } from "../rendering/form/ActionToggle";
import ScrapingFilterTable from "./ScrapingFilterTable";
import DismissExpiredModal from "./DismissExpiredModal";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAlert } from "../../contexts/AlertContext";
import { useProgressOverlay } from "../../contexts/useProgressOverlayContext";
import { ApiResponse, ApiResponsePromise } from "../../services/api/Base";
import { MOBILE_BREAKPOINT, TABLET_BREAKPOINT } from "../../utils/Breakpoints";
import { useViewport } from "../../contexts/ViewportContext";
import { scrapedJobApi } from "../../services/api/Services";

interface ScrapedJobTableProps extends DataTableProps {
	favouritesOnly?: boolean;
	dashboardMode?: boolean;
}

const ScrapedJobsTable: React.FC<ScrapedJobTableProps> = ({
	columns = [],
	title = undefined,
	onTotalCountChange,
	reloadTrigger,
	favouritesOnly = false,
	dashboardMode = false,
}: ScrapedJobTableProps): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();
	const { updateEntity } = dataContext;
	const { currentUser, token } = useAuth();
	const { showDelete } = useAlert();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const tableRef = useRef<DataTableHandle>(null);
	const [showFilters, setShowFilters] = useState<boolean>(false);
	const [showFavouriteFilters, setShowFavouriteFilters] = useState<boolean>(false);
	const [expiredJobs, setExpiredJobs] = useState<ScrapedJobData[]>([]);
	const [showDismissExpiredModal, setShowDismissExpiredModal] = useState<boolean>(false);
	const [showPastDeadline, setShowPastDeadline] = useState<boolean>(false);
	const [internalReloadTrigger, setInternalReloadTrigger] = useState<number>(0);
	const [locallyReadIds, setLocallyReadIds] = useState<Set<number>>(new Set());
	const filtersInitializedRef = useRef(false);
	const [windowWidth, setWindowWidth] = useState(window.innerWidth);
	const { showProgress, hideProgress } = useProgressOverlay();
	const { isMobile } = useViewport();

	useEffect(() => {
		const handleResize = (): void => setWindowWidth(window.innerWidth);
		window.addEventListener("resize", handleResize);
		return () => window.removeEventListener("resize", handleResize);
	}, []);

	const handleDismissExpired = useCallback(async (): Promise<void> => {
		if (!token) return;
		showProgress("Loading expired alerts, please wait.", "Loading expired alerts...");
		try {
			const response: ApiResponse<ScrapedJobData[]> = await scrapedJobApi.getExpired(token);
			if (response.data.length === 0) {
				showToastSuccess("No expired job alerts found.");
				return;
			}
			setExpiredJobs(response.data);
			setShowDismissExpiredModal(true);
		} catch {
			showToastError("Failed to load expired alerts. Please try again.");
		} finally {
			hideProgress();
		}
	}, [showProgress, hideProgress, showToastSuccess, showToastError, token]);

	const handleConfirmDismissExpired = useCallback(
		async (ids: number[]): Promise<void> => {
			setShowDismissExpiredModal(false);
			showProgress("Dismissing expired alerts, please wait.", "Dismissing expired alerts…");
			try {
				await Promise.all(
					ids.map(
						(id: number): ApiResponsePromise<JamData> =>
							updateEntity("scrapedJob", id, { is_active: false })
					)
				);
				const n = ids.length;
				showToastSuccess(`${n} expired job alert${n !== 1 ? "s" : ""} dismissed.`);
				tableRef.current?.clearSelection();
				setInternalReloadTrigger((t: number): number => t + 1);
			} catch {
				showToastError("Failed to dismiss expired alerts. Please try again.");
			} finally {
				hideProgress();
			}
		},
		[updateEntity, showProgress, hideProgress, showToastSuccess, showToastError]
	);

	const handleBulkDismiss = useCallback(
		async (ids: number[]): Promise<void> => {
			const n = `${ids.length} alert${ids.length > 1 ? "s" : ""}`;
			const confirmed: boolean = await showDelete({
				title: "Delete Job Alerts",
				message: `Delete ${n} job alerts?`,
				confirmText: "Delete",
				cancelText: "Cancel",
			});
			if (confirmed) {
				showProgress(`Dismissing ${n}, please wait.`, "Dismissing alerts…");
				try {
					await Promise.all(
						ids.map(
							(id: number): ApiResponsePromise<JamData> =>
								updateEntity("scrapedJob", id, { is_active: false })
						)
					);
					showToastSuccess(`${n} job alerts dismissed.`);
					tableRef.current?.clearSelection();
					setInternalReloadTrigger((t: number): number => t + 1);
				} catch {
					showToastError("Failed to delete some alerts. Please try again.");
				} finally {
					hideProgress();
				}
			}
		},
		[updateEntity, showDelete, showToastSuccess, showToastError]
	);

	useEffect(() => {
		if (!favouritesOnly) return;
		if (!filtersInitializedRef.current) {
			filtersInitializedRef.current = true;
			return;
		}
		setInternalReloadTrigger((t) => t + 1);
	}, [dataContext.scrapingFavouriteFilters]);

	const queryParams = useMemo(
		() => ({
			show_past_deadline: showPastDeadline.toString(),
			...(favouritesOnly ? { favourites_only: "true" } : {}),
		}),
		[showPastDeadline, favouritesOnly]
	);
	let defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn(),
					tableColumns.scrapedCompanyColumn(),
					tableColumns.scrapedLocationColumn(),
					tableColumns.salaryRangeColumn(),
					tableColumns.overallScore(),
					tableColumns.urlGenericColumn(),
					tableColumns.platformColumn(),
					tableColumns.scrapingStatusColumn(),
					tableColumns.createdAtColumn({ label: "Date Received" }),
				];

	if (dashboardMode && windowWidth < TABLET_BREAKPOINT) {
		defaultColumns = defaultColumns.filter((col) => !["location", "url", "created_at"].includes(col.key));
	}
	if (dashboardMode && windowWidth < MOBILE_BREAKPOINT) {
		defaultColumns = defaultColumns.filter((col) => !["company", "is_processed"].includes(col.key));
	}

	return (
		<>
			<DataTable
				ref={tableRef}
				title={title}
				entityType="scrapedJob"
				onTotalCountChange={onTotalCountChange}
				mode="import"
				columns={defaultColumns}
				initialSortConfig={{ key: "created_at", direction: "desc" }}
				Modal={ScrapedJobModal}
				endpoint="scraped-jobs"
				modalSize="xl"
				showAdd={false}
				showSearch={true}
				smallSearch={dashboardMode}
				queryParams={queryParams}
				enableColumnConfig={!dashboardMode}
				reloadTrigger={(reloadTrigger ?? 0) + internalReloadTrigger}
				rowIndicator={(item: ScrapedJobData): boolean =>
					!!currentUser?.previous_login && item.created_at > currentUser.previous_login
				}
				rowReadIndicator={(item: ScrapedJobData): boolean =>
					!locallyReadIds.has(item.id) &&
					(!item.read_at || item.read_at < item.created_at || item.read_at < item.scrape_datetime)
				}
				onItemOpen={(item: ScrapedJobData): void => {
					if (!item.read_at || item.read_at < item.created_at || item.read_at < item.scrape_datetime) {
						setLocallyReadIds((prev) => new Set([...prev, item.id]));
						updateEntity("scrapedJob", item.id, { read_at: new Date() });
					}
				}}
				enableMultiSelect={!dashboardMode}
				bulkActions={
					dashboardMode
						? []
						: [
								{
									id: "bulk-action-delete",
									label: "Delete",
									icon: "x-circle",
									variant: "outline-danger",
									onClick: (ids: number[]): Promise<void> => handleBulkDismiss(ids),
								},
								{ type: "divider" as const },
								{
									id: "bulk-action-delete-expired",
									label: "Delete Expired",
									icon: "calendar-x",
									variant: "outline-danger",
									onClick: (): Promise<void> => handleDismissExpired(),
								},
							]
				}
				toolbarAddon={
					<div style={{ flex: 1, display: "flex", alignItems: "center", gap: "0.75rem", height: "100%" }}>
						{!favouritesOnly && !dashboardMode && (
							<Button
								style={{ height: "100%" }}
								variant="outline-primary"
								onClick={(): void => setShowFilters(true)}
								id={"scraping-filters-button"}
								title="Scraping Filters"
							>
								{isMobile ? (
									<i className="bi bi-funnel-fill"></i>
								) : (
									<>
										Scraping Filters (
										{
											dataContext.scrapingFilters.filter(
												(filter: ScrapingFilterData): boolean => filter.is_active
											).length
										}
										)
									</>
								)}
							</Button>
						)}
						{favouritesOnly && (
							<Button
								style={{ height: "100%", padding: "0.3rem" }}
								variant="outline-primary"
								onClick={(): void => setShowFavouriteFilters(true)}
								id={"favourite-filters-button"}
							>
								Favourite Filters (
								{
									dataContext.scrapingFavouriteFilters.filter(
										(filter: ScrapingFilterData): boolean => filter.is_active
									).length
								}
								)
							</Button>
						)}
						<ActionToggle
							id="show-past-deadline-toggle"
							label="Show past deadline jobs"
							checked={showPastDeadline}
							onChange={(): void => setShowPastDeadline((prev: boolean): boolean => !prev)}
						/>
					</div>
				}
			/>
			<ScrapingFilterTable
				show={showFilters}
				onHide={(): void => {
					setShowFilters(false);
				}}
			/>
			<ScrapingFilterTable
				variant="favourite"
				show={showFavouriteFilters}
				onHide={(): void => {
					setShowFavouriteFilters(false);
				}}
			/>
			<DismissExpiredModal
				show={showDismissExpiredModal}
				jobs={expiredJobs}
				onConfirm={handleConfirmDismissExpired}
				onHide={(): void => setShowDismissExpiredModal(false)}
			/>
		</>
	);
};

export default ScrapedJobsTable;
