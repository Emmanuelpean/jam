import React from "react";
import { DataTableProps, DataTable } from "./DataTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { JobApplicationUpdateModal, JobApplicationUpdateModalProps } from "../modals/JobApplicationUpdateModal";

interface JobApplicationUpdatesTableProps extends DataTableProps {
	jobId: number;
}

const JobApplicationUpdatesTable: React.FC<JobApplicationUpdatesTableProps> = ({ jobId, data = [], columns = [] }) => {
	const defaultColumns =
		columns.length > 0
			? columns
			: [tableColumns.dateColumn(), tableColumns.updateTypeColumn(), tableColumns.noteColumn()];

	const ModalWithProps = (props: JobApplicationUpdateModalProps) => (
		<JobApplicationUpdateModal {...props} jobId={jobId} />
	);

	return (
		<DataTable
			entityType="jobApplicationUpdates"
			data={data}
			columns={defaultColumns}
			initialSortConfig={{ key: "date", direction: "desc" }}
			Modal={ModalWithProps}
			nameKey="date"
			itemType="Update"
			modalSize="lg"
			showAllEntries={true}
			compact={true}
		/>
	);
};

export default JobApplicationUpdatesTable;
