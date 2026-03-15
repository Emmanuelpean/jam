import React, { JSX, useCallback, useMemo, useRef, useState } from "react";
import { Button } from "react-bootstrap";
import { DataTable, DataTableHandle, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../DataModal/ScrapedJobModal";
import { ScrapingFilterData } from "../../services/schemas/Services";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { useAuth } from "../../contexts/AuthContext";
import { ActionToggle } from "../rendering/form/ActionToggle";
import ScrapingFilterTable from "./ScrapingFilterTable";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAlert } from "../../contexts/AlertContext";
import { ProgressOverlay } from "../ProgressOverlay/ProgressOverlay";

const ScrapedJobsTable: React.FC<DataTableProps> = ({
	columns = [],
	title = undefined,
}: DataTableProps): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();
	const { currentUser } = useAuth();
	const { updateEntity } = dataContext;
	const { showDelete } = useAlert();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const tableRef = useRef<DataTableHandle>(null);
	const [showFilters, setShowFilters] = useState<boolean>(false);
	const [showPastDeadline, setShowPastDeadline] = useState<boolean>(false);
	const [sincePreviousLogin, setSincePreviousLogin] = useState<boolean>(false);
	const [reloadTrigger, setReloadTrigger] = useState<number>(0);
	const [progress, setProgress] = useState<{ show: boolean; title: string; message: string }>({
		show: false, title: "", message: "",
	});

	const n = (ids: string[]) => `${ids.length} alert${ids.length > 1 ? "s" : ""}`;

	const handleBulkDismiss = useCallback(async (ids: string[]) => {
		const confirmed = await showDelete({
			title: "Dismiss Job Alerts",
			message: `Dismiss ${n(ids)}? They will no longer appear in your alerts.`,
			confirmText: "Dismiss",
			cancelText: "Cancel",
		});
		if (!confirmed) return;
		setProgress({ show: true, title: "Dismissing alerts…", message: `Dismissing ${n(ids)}, please wait.` });
		try {
			await Promise.all(ids.map((id) => updateEntity("scrapedJob", Number(id), { is_active: false })));
			showToastSuccess(`${n(ids)} dismissed.`);
			tableRef.current?.clearSelection();
			setReloadTrigger((t) => t + 1);
		} catch {
			showToastError("Failed to dismiss some alerts. Please try again.");
		} finally {
			setProgress((p) => ({ ...p, show: false }));
		}
	}, [updateEntity, showDelete, showToastSuccess, showToastError]);

	const queryParams = useMemo(
		() => ({
			show_past_deadline: showPastDeadline.toString(),
			since_last_login: sincePreviousLogin.toString(),
		}),
		[showPastDeadline, sincePreviousLogin]
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
					tableColumns.createdAtColumn({ label: "Date Received" }),
				];

	return (
		<>
			<DataTable
				ref={tableRef}
				title={title}
				entityType="scrapedJob"
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
				reloadTrigger={reloadTrigger}
				enableMultiSelect={true}
				bulkActions={[
					{ label: "Dismiss", icon: "x-circle", variant: "outline-danger", onClick: (ids) => handleBulkDismiss(ids) },
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
						<ActionToggle
							id="since-last-login-toggle"
							label="Since last login"
							checked={sincePreviousLogin}
							onChange={(): void => setSincePreviousLogin((prev: boolean): boolean => !prev)}
							disabled={!currentUser?.previous_login}
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
			<ProgressOverlay show={progress.show} title={progress.title} message={progress.message} />
		</>
	);
};

export default ScrapedJobsTable;
