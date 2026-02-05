import React, { JSX, useState } from "react";
import { Button } from "react-bootstrap";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../DataModal/ScrapedJobModal";
import { ScrapingFilterData } from "../../services/schemas/Services";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import ScrapingFilterTable from "./ScrapingFilterTable";

const ScrapedJobsTable: React.FC<DataTableProps> = ({
	columns = [],
	title = undefined,
}: DataTableProps): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();
	const [showFilters, setShowFilters] = useState(false);
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
				toolbarAddon={
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
