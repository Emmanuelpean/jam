import React from "react";
import GenericTableWithModals from "../components/tables/GenericTableWithModals";
import JobApplicationFormModal from "../components/modals/job_application/JobApplicationFormModal";
import JobApplicationViewModal from "../components/modals/job_application/JobApplicationViewModal";
import { useTableData } from "../components/tables/Table";
import { columns } from "../components/rendering/ColumnRenders";

const JobApplicationsPage = () => {
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
		columns.url(),
		columns.createdAt(),
	];

	return (
		<GenericTableWithModals
			title="Job Applications"
			data={jobApplications}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			addButtonText="Add Job Application"
			loading={loading}
			error={error}
			emptyMessage="No job applications found"
			FormModal={JobApplicationFormModal}
			ViewModal={JobApplicationViewModal}
			endpoint="jobapplications"
			nameKey="title"
			itemType="Job Application"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setJobApplications}
			formModalSize="xl"
			viewModalSize="xl"
		/>
	);
};

export default JobApplicationsPage;
