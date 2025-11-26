import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../modals/ScrapedJobModal";
import { scrapedJobApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { ScrapedJobData } from "../../services/Schemas";

const ScrapedJobsTable: React.FC<DataTableProps> = ({ columns = [] }: DataTableProps): JSX.Element => {
	const { token } = useAuth();
	const defaultColumns =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn(),
					tableColumns.scrapedCompanyColumn(),
					tableColumns.scrapedLocationColumn(),
					tableColumns.salaryRangeColumn(),
					tableColumns.descriptionColumn(),
					tableColumns.urlGenericColumn(),
					tableColumns.platformColumn(),
					tableColumns.createdAtColumn({ label: "Date Received" }),
				];

	const onImportSuccess = (importedData: ScrapedJobData): Promise<any> => {
		if (token) {
			return scrapedJobApi.update(importedData.id, { is_imported: true }, token);
		} else {
			return Promise.reject("No auth token available");
		}
	};

	return (
		<DataTable
			entityType="scrapedJobs"
			mode="import"
			columns={defaultColumns}
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			Modal={ScrapedJobModal}
			endpoint="scraped_jobs"
			nameKey="title"
			itemType="Scraped Job"
			modalSize="xl"
			showAdd={false}
			showSearch={true}
			onImportSuccess={onImportSuccess}
		/>
	);
};

export default ScrapedJobsTable;
