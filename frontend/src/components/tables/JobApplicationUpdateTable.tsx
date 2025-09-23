import React from "react";
import { GenericTable, GenericTableProps, DataTableProps } from "./GenericTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobApplicationUpdateModal, JobApplicationUpdateModalProps } from "../modals/JobApplicationUpdateModal";
import { JobApplicationUpdateData } from "../../services/Schemas";

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

	const handleDataChange = (newData: JobApplicationUpdateData[]) => {
		onDataChange?.(newData);
	};

	return (
		<GenericTable
			mode="controlled"
			data={data}
			onDataChange={handleDataChange}
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
