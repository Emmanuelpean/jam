import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobEmailModal } from "../DataModal/JobEmailModal";

const JobEmailTable: React.FC<DataTableProps> = ({
	columns = [],
	title = undefined,
	onTotalCountChange,
	reloadTrigger,
}: DataTableProps): JSX.Element => {
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn({ key: "subject", label: "Subject" }),
					tableColumns.senderColumn(),
					tableColumns.platformColumn(),
					tableColumns.alertNameColumn(),
					tableColumns.jobsFoundColumn(),
					tableColumns.dateReceivedColumn(),
				];

	return (
		<DataTable
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
		/>
	);
};

export default JobEmailTable;
