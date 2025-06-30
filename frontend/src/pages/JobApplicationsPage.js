import React from "react";
import JobApplicationFormModal from "../components/modals/job_application/JobApplicationFormModal";
import JobApplicationViewModal from "../components/modals/job_application/JobApplicationViewModal";
import {useTableData, GenericTableWithModals} from "../components/tables/TableSystem";
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
			loading={loading}
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
			formModalSize="xl"
			viewModalSize="xl"
		/>
	);
};

export default JobApplicationsPage;
