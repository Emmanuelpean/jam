import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobEmailModal } from "../DataModal/JobEmailModal";
import { renderFunctions, RenderParams } from "../rendering/view/ViewRenders";
import { JobEmailData } from "../../services/schemas/Services";

const JobEmailTableReadOnly: React.FC<DataTableProps> = ({
	data = [],
	columns = [],
	modalProps,
}: DataTableProps): JSX.Element => {
	const defaultColumns: TableColumn<JobEmailData>[] =
		columns.length > 0
			? (columns as TableColumn<JobEmailData>[])
			: [
					tableColumns.subjectColumn<JobEmailData>(),
					{ key: "sender", label: "Sender", sortable: true, searchable: true, type: "text" } as TableColumn<JobEmailData>,
					tableColumns.platformColumn<JobEmailData>(),
					{
						key: "alert_name",
						label: "Alert Name",
						sortable: true,
						searchable: true,
						type: "text",
					} as TableColumn<JobEmailData>,
					{
						key: "date_received",
						label: "Date Received",
						sortable: true,
						type: "date",
						render: (params: RenderParams) => renderFunctions._date(params, "date_received"),
					} as TableColumn<JobEmailData>,
				];

	return (
		<DataTable<JobEmailData>
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
