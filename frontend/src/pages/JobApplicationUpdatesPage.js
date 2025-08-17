import React, { useEffect } from "react";
import {
	JobApplicationUpdateFormModal,
	JobApplicationUpdateViewModal,
} from "../components/modals/JobApplicationUpdateModal";
import { GenericTableWithModals, useTableData } from "../components/tables/TableSystem";
import { columns } from "../components/rendering/ColumnRenders";
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
	} = useTableData("jobapplicationupdates");

	const tableColumns = [
		columns.jobApplicationJob(),
		columns.date(),
		columns.updateType(),
		columns.note(),
		columns.createdAt(),
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
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
			FormModal={JobApplicationUpdateFormModal}
			ViewModal={JobApplicationUpdateViewModal}
			endpoint="jobapplicationupdates"
			nameKey="note"
			itemType="Job Application Update"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setJobApplicationUpdates}
			ModalSize="lg"
		/>
	);
};

export default JobApplicationUpdatesPage;
