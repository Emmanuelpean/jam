import React from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/TableSystem";
import { InterviewFormModal, InterviewViewModal } from "../components/modals/interview/InterviewModal";
import { columns } from "../components/rendering/ColumnRenders";

const InterviewsPage = () => {
	const {
		data: interviews,
		setData: setInterviews,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("interviews");

	const tableColumns = [
		columns.jobApplicationJob(),
		columns.interviewers(),
		columns.date(),
		columns.type(),
		columns.location(),
		columns.createdAt(),
	];

	return (
		<GenericTableWithModals
			title="Interviews"
			data={interviews}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			addButtonText="Add Interview"
			loading={loading}
			error={error}
			emptyMessage="No interviews found"
			FormModal={InterviewFormModal}
			ViewModal={InterviewViewModal}
			endpoint="interviews"
			nameKey="date"
			itemType="Interview"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setInterviews}
		/>
	);
};

export default InterviewsPage;
