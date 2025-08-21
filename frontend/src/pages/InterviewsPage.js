import React, { useEffect } from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/TableSystem";
import { InterviewFormModal, InterviewViewModal } from "../components/modals/InterviewModal";
import { columns } from "../components/rendering/ColumnRenders";
import { useLoading } from "../contexts/LoadingContext";

const InterviewsPage = () => {
	const { showLoading, hideLoading } = useLoading();
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
	} = useTableData("interviews", [], {}, { key: "date", direction: "desc" });

	const tableColumns = [
		columns.jobApplicationJob(),
		columns.interviewers(),
		columns.date(),
		columns.type(),
		columns.location(),
		columns.createdAt(),
	];

	useEffect(() => {
		if (loading) {
			showLoading("Loading Interviews...");
		} else {
			hideLoading();
		}
		return () => {
			hideLoading();
		};
	}, [loading, showLoading, hideLoading]);

	return (
		<GenericTableWithModals
			title="Interviews"
			data={interviews}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
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
