import React, { useEffect } from "react";
import { JobApplicationUpdateModal } from "../components/modals/JobApplicationUpdateModal";
import { GenericTableWithModals, useTableData } from "../components/tables/GenericTable";
import { tableColumns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext";

const JobApplicationUpdatesPage = () => {
	const { showLoading, hideLoading } = useLoading();
	const {
		data: jobApplicationUpdates,
		setData: setJobApplicationUpdates,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("jobapplicationupdates", [], {}, { key: "date", direction: "desc" });

	const columns = [
		tableColumns.job!(),
		tableColumns.date!(),
		tableColumns.updateType!(),
		tableColumns.note!(),
		tableColumns.createdAt!(),
	];

	useEffect(() => {
		if (loading) {
			showLoading("Loading Job Application Updates...");
		} else {
			hideLoading();
		}
		return () => {
			hideLoading();
		};
	}, [loading, showLoading, hideLoading]);

	return (
		<GenericTableWithModals
			title="Job Application Updates"
			data={jobApplicationUpdates}
			columns={columns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
			Modal={JobApplicationUpdateModal}
			endpoint="jobapplicationupdates"
			nameKey="date"
			itemType="Job Application Update"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setJobApplicationUpdates}
			modalSize="lg"
		/>
	);
};

export default JobApplicationUpdatesPage;
