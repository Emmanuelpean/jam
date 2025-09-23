import React from "react";
import { GenericTable, DataTableProps } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { InterviewModal, InterviewModalProps } from "../modals/InterviewModal";
import { DataModalProps } from "../modals/GenericModal/GenericModal";
import { InterviewData } from "../../services/Schemas";

interface InterviewsTableProps extends DataTableProps {
	jobId?: number;
}

const InterviewsTable: React.FC<InterviewsTableProps> = ({
	jobId,
	data = [],
	onDataChange,
	error = null,
	columns = [],
	showAdd = true,
}) => {
	const defaultColumns =
		columns.length > 0
			? columns
			: [tableColumns.date(), tableColumns.type(), tableColumns.location(), tableColumns.note()];

	const ModalWithProps: React.FC<DataModalProps> = (props: InterviewModalProps) => (
		<InterviewModal {...props} jobId={jobId} />
	);

	const handleDataChange = (newData: InterviewData[]) => {
		console.log("newData are", newData);
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
			endpoint="interviews"
			nameKey="date"
			itemType="Interview"
			modalSize="lg"
			showAllEntries={true}
			compact={true}
			showAdd={showAdd}
		/>
	);
};

export default InterviewsTable;
