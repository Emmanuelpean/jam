import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobEmailModal } from "../DataModal/JobEmailModal";
import { JobEmailData } from "../../services/schemas/Services";

interface JobEmailTableProps extends DataTableProps {
	queryParams?: Record<string, string>;
}

const JobEmailTable: React.FC<JobEmailTableProps> = ({
	columns = [],
	title = undefined,
	onTotalCountChange,
	reloadTrigger,
	queryParams,
}: JobEmailTableProps): JSX.Element => {
	const defaultColumns: TableColumn<JobEmailData>[] =
		columns.length > 0
			? (columns as TableColumn<JobEmailData>[])
			: [
					tableColumns.subjectColumn<JobEmailData>(),
					tableColumns.platformColumn<JobEmailData>(),
					tableColumns.alertNameColumn<JobEmailData>(),
					tableColumns.jobsFoundColumn<JobEmailData>(),
					tableColumns.dateReceivedColumn<JobEmailData>(),
				];

	return (
		<DataTable<JobEmailData>
			title={title}
			entityType="jobEmail"
			onTotalCountChange={onTotalCountChange}
			mode="default"
			columns={defaultColumns}
			initialSortConfig={{ key: "date_received", direction: "desc" }}
			Modal={JobEmailModal}
			endpoint="job-alert-emails"
			modalSize="xl"
			showAdd={false}
			showSearch={true}
			enableColumnConfig={true}
			menuItems={["view"]}
			reloadTrigger={reloadTrigger}
			queryParams={queryParams}
		/>
	);
};

export default JobEmailTable;
