import React, { JSX, useMemo, useState } from "react";
import { Button } from "react-bootstrap";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../DataModal/ScrapedJobModal";
import { ScrapingFilterData } from "../../services/schemas/Services";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { useAuth } from "../../contexts/AuthContext";
import { ActionToggle } from "../rendering/form/ActionToggle";
import ScrapingFilterTable from "./ScrapingFilterTable";

const ScrapedJobsTable: React.FC<DataTableProps> = ({
	columns = [],
	title = undefined,
}: DataTableProps): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();
	const { currentUser } = useAuth();
	const [showFilters, setShowFilters] = useState(false);
	const [showPastDeadline, setShowPastDeadline] = useState(false);
	const [sinceLastLogin, setSinceLastLogin] = useState(false);

	const queryParams = useMemo(
		() => ({
			show_past_deadline: showPastDeadline.toString(),
			since_last_login: sinceLastLogin.toString(),
		}),
		[showPastDeadline, sinceLastLogin]
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
				toolbarAddon={
					<div style={{ flex: 1, display: "flex", alignItems: "center", gap: "0.75rem" }}>
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
							label="Show past deadline"
							checked={showPastDeadline}
							onChange={() => setShowPastDeadline((prev) => !prev)}
						/>
						<ActionToggle
							id="since-last-login-toggle"
							label="Since last login"
							checked={sinceLastLogin}
							onChange={() => setSinceLastLogin((prev) => !prev)}
							disabled={!currentUser?.last_login}
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
