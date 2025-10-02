import React from "react";
import { DataTableProps, DataTable } from "./DataTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { JobApplicationUpdateModal, JobApplicationUpdateModalProps } from "../modals/JobApplicationUpdateModal";

interface JobApplicationUpdatesTableProps extends DataTableProps {
	jobId: string | number;
}

const JobApplicationUpdatesTable: React.FC<JobApplicationUpdatesTableProps> = ({
	jobId,
	data = [],
	onDataChange,
	error = null,
	columns = [],
}) => {
	const defaultColumns =
		columns.length > 0 ? columns : [tableColumns.date(), tableColumns.updateType(), tableColumns.note()];

	const ModalWithProps = (props: JobApplicationUpdateModalProps) => (
		<JobApplicationUpdateModal {...props} jobId={jobId} />
	);

	return (
		<DataTable
			mode="controlled"
			data={data}
			onDataChange={onDataChange}
			error={error}
			columns={defaultColumns}
			initialSortConfig={{ key: "date", direction: "desc" }}
			Modal={ModalWithProps}
			endpoint="jobapplicationupdates"
			nameKey="date"
			itemType="Update"
			modalSize="lg"
			showAllEntries={true}
			compact={true}
		/>
	);
};

export default JobApplicationUpdatesTable;
