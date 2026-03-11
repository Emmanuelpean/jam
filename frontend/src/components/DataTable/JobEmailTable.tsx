import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobEmailModal } from "../DataModal/JobEmailModal";
import { renderFunctions, RenderParams } from "../rendering/view/ViewRenders";

const JobEmailTable: React.FC<DataTableProps> = ({ columns = [], title = undefined, onTotalCountChange }: DataTableProps): JSX.Element => {
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn({ key: "subject", label: "Subject" }),
					{ key: "sender", label: "Sender", sortable: true, searchable: true, type: "text" } as TableColumn,
					tableColumns.platformColumn(),
					{ key: "alert_name", label: "Alert Name", sortable: true, searchable: true, type: "text" } as TableColumn,
					{ key: "job_found_n", label: "Jobs Found", sortable: true, type: "number" } as TableColumn,
					{
						key: "date_received",
						label: "Date Received",
						sortable: true,
						type: "date",
						render: (params: RenderParams) => renderFunctions._date(params, "date_received"),
					} as TableColumn,
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
			modalSize="lg"
			showAdd={false}
			showSearch={true}
			menuItems={["view"]}
		/>
	);
};

export default JobEmailTable;