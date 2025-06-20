import React from "react";
import GenericTableWithModals from "../components/tables/GenericTableWithModals";
import InterviewFormModal from "../components/modals/interview/InterviewFormModal";
import InterviewViewModal from "../components/modals/interview/InterviewViewModal";
import { useTableData } from "../components/tables/Table";
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

	const tableColumns = [columns.interviewers, columns.date, columns.type, columns.location, columns.createdAt];

	// Create wrapper component for ViewModal
	const InterviewViewModalWithProps = (props) => (
		<InterviewViewModal
			{...props}
			interview={props.item} // Map 'item' to 'interview'
		/>
	);

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
			ViewModal={InterviewViewModalWithProps}
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
