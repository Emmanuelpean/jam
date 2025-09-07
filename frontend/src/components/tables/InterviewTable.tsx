import React from "react";
import { GenericTableWithModals, useProvidedTableData } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumnRenders";
import { InterviewModal } from "../modals/InterviewModal";

interface InterviewsTableProps {
	jobApplicationId: number;
	onChange?: () => void;
	data?: any[] | null;
}

interface Interview {
	id: number;
	date: string;
	type: string;
	location: string;
	note: string;
	job_application_id: number;
	// Add other interview properties as needed
}

interface ModalProps {
	submode: "add" | "edit" | "view";
	onSuccess?: (item: Interview) => void;
}

const InterviewsTable: React.FC<InterviewsTableProps> = ({ jobApplicationId, onChange, data = null }) => {
	const {
		data: interviewData,
		loading,
		error,
		addItem,
		sortConfig,
		setSortConfig,
		updateItem,
		removeItem,
	} = useProvidedTableData(data, { key: "date", direction: "desc" });

	const ViewColumns = [tableColumns.date!(), tableColumns.type!(), tableColumns.location!(), tableColumns.note!()];

	const ModalWithProps: React.FC<ModalProps> = (
		props, // @ts-ignore // TODO
	) => <InterviewModal {...props} jobApplicationId={jobApplicationId} />;

	return (
		<GenericTableWithModals
			data={interviewData}
			columns={ViewColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			loading={loading}
			error={error}
			Modal={ModalWithProps}
			endpoint="interviews"
			nameKey="date"
			itemType="Interview"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={() => {}}
			ModalSize="lg"
			showAllEntries={true}
			compact={true}
		/>
	);
};

export default InterviewsTable;
