import React, { useEffect } from "react";
import {
	JobApplicationFormModal,
	JobApplicationViewModal,
} from "../components/modals/job_application/JobApplicationModal";
import { GenericTableWithModals, useTableData } from "../components/tables/TableSystem";
import { columns } from "../components/rendering/ColumnRenders";
import { useLoading } from "../contexts/LoadingContext";

const JobApplicationsPage = () => {
	const { showLoading, hideLoading } = useLoading();
	const {
		data: jobApplications,
		setData: setJobApplications,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("jobapplications");

	const tableColumns = [
		columns.date(),
		columns.job(),
		columns.status(),
		columns.interviewCount(),
		columns.files(),
		columns.url({ label: "URL" }),
		columns.createdAt(),
	];

	useEffect(() => {
		if (loading) {
			showLoading("Loading Job Applications...");
		} else {
			hideLoading();
		}
		return () => {
			hideLoading();
		};
	}, [loading, showLoading, hideLoading]);

	return (
		<GenericTableWithModals
			title="Job Applications"
			data={jobApplications}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
			FormModal={JobApplicationFormModal}
			ViewModal={JobApplicationViewModal}
			endpoint="jobapplications"
			nameKey="title"
			itemType="Job Application"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setJobApplications}
			ModalSize="xl"
		/>
	);
};

export default JobApplicationsPage;
