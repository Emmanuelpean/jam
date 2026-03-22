import React, { JSX, useCallback, useMemo, useRef, useState } from "react";
import { Button } from "react-bootstrap";
import { DataTable, DataTableHandle, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../DataModal/ScrapedJobModal";
import { ScrapedJobData, ScrapingFilterData } from "../../services/schemas/Services";
import { DataContextValue, JamData, useDataContext } from "../../contexts/DataContext";
import { useAuth } from "../../contexts/AuthContext";
import { ActionToggle } from "../rendering/form/ActionToggle";
import ScrapingFilterTable from "./ScrapingFilterTable";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAlert } from "../../contexts/AlertContext";
import { useProgressOverlay } from "../../contexts/useProgressOverlayContext";
import { ApiResponsePromise } from "../../services/api/Base";

const ScrapedJobsTable: React.FC<DataTableProps> = ({
	columns = [],
	title = undefined,
	onTotalCountChange,
	reloadTrigger,
}: DataTableProps): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();
	const { updateEntity } = dataContext;
	const { currentUser } = useAuth();
	const { showDelete } = useAlert();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const tableRef = useRef<DataTableHandle>(null);
	const [showFilters, setShowFilters] = useState<boolean>(false);
	const [showPastDeadline, setShowPastDeadline] = useState<boolean>(false);
	const [internalReloadTrigger, setInternalReloadTrigger] = useState<number>(0);
	const { showProgress, hideProgress } = useProgressOverlay();

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

	const queryParams = useMemo(
		() => ({
			show_past_deadline: showPastDeadline.toString(),
		}),
		[showPastDeadline]
	);
	const defaultColumns: TableColumn[] =
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
				queryParams={queryParams}
				enableColumnConfig={true}
				reloadTrigger={(reloadTrigger ?? 0) + internalReloadTrigger}
				rowIndicator={(item: ScrapedJobData): boolean =>
					!!currentUser?.previous_login &&
					new Date(item.created_at) > new Date(currentUser.previous_login as string)
				}
				rowReadIndicator={(item: ScrapedJobData): boolean =>
					!item.read_at || new Date(item.read_at) < new Date(item.modified_at as string)
				}
				onItemOpen={(item: ScrapedJobData): void => {
					if (!item.read_at) {
						updateEntity("scrapedJob", item.id, { read_at: new Date().toISOString() });
					}
				}}
				enableMultiSelect={true}
				bulkActions={[
					{
						label: "Delete",
						icon: "x-circle",
						variant: "outline-danger",
						onClick: (ids: number[]): Promise<void> => handleBulkDismiss(ids),
					},
				]}
				toolbarAddon={
					<div style={{ flex: 1, display: "flex", alignItems: "center", gap: "0.75rem", height: "100%" }}>
						<Button
							style={{ height: "100%" }}
							variant="outline-primary"
							onClick={(): void => setShowFilters(true)}
							id={"scraping-filters-button"}
						>
							Scraping Filters (
							{
								dataContext.scrapingFilters.filter(
									(filter: ScrapingFilterData): boolean => filter.is_active
								).length
							}
							)
						</Button>
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
		</>
	);
};

export default ScrapedJobsTable;
