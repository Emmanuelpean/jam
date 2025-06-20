import React from "react";
import { useTableData } from "../components/tables/Table";
import GenericTableWithModals from "../components/tables/GenericTableWithModals";
import JobFormModal from "../components/modals/job/JobFormModal";
import JobViewModal from "../components/modals/job/JobViewModal";
import { columns } from "../components/rendering/ColumnRenders";

const JobsPage = () => {
	const {
		data: jobs,
		setData: setJobs,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("jobs");

	const tableColumns = [
		columns.title,
		columns.company,
		columns.location,
		columns.url,
		columns.salaryRange,
		columns.personalRating,
		columns.jobapplication,
		columns.createdAt,
	];

	return (
		<GenericTableWithModals
			title="Jobs"
			data={jobs}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			addButtonText="Add Job"
			loading={loading}
			error={error}
			emptyMessage="No job found"
			FormModal={JobFormModal}
			ViewModal={JobViewModal}
			endpoint="jobs"
			nameKey="title"
			itemType="Job"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setJobs}
			formModalSize="xl"
			viewModalSize="xl"
		/>
	);
};

export default JobsPage;