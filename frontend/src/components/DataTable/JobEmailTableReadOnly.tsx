import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobEmailModal } from "../DataModal/JobEmailModal";
import { renderFunctions, RenderParams } from "../rendering/view/ViewRenders";

const JobEmailTableReadOnly: React.FC<DataTableProps> = ({
	data = [],
	columns = [],
	modalProps,
}: DataTableProps): JSX.Element => {
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.subjectColumn(),
					{ key: "sender", label: "Sender", sortable: true, searchable: true, type: "text" } as TableColumn,
					tableColumns.platformColumn(),
					{
						key: "alert_name",
						label: "Alert Name",
						sortable: true,
						searchable: true,
						type: "text",
					} as TableColumn,
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
			entityType="jobEmail"
			columns={defaultColumns}
			initialSortConfig={{ key: "date_received", direction: "desc" }}
			Modal={JobEmailModal}
			data={data}
			modalSize="xl"
			compact={true}
			showAdd={false}
			showSearch={false}
			menuItems={["view"]}
			modalProps={modalProps}
		/>
	);
};

export default JobEmailTableReadOnly;
