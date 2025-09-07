import React, { useEffect } from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/GenericTable";
import { InterviewModal } from "../components/modals/InterviewModal";
import { tableColumns } from "../components/rendering/view/TableColumnRenders";
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

	const columns = [
		tableColumns.jobApplicationJob!(),
		tableColumns.interviewers!(),
		tableColumns.date!(),
		tableColumns.type!(),
		tableColumns.location!(),
		tableColumns.createdAt!(),
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
			columns={columns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
			Modal={InterviewModal}
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
