import React from "react";
import { useTableData, GenericTableWithModals } from "../components/tables/TableSystem";
import { JobFormModal, JobViewModal } from "../components/modals/job/JobModal";
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
		columns.title(),
		columns.company(),
		columns.location(),
		columns.url(),
		columns.salaryRange(),
		columns.personalRating(),
		columns.jobapplication(),
		columns.createdAt(),
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
			loading={loading}
			error={error}
			FormModal={JobFormModal}
			ViewModal={JobViewModal}
			endpoint="jobs"
			nameKey="title"
			itemType="Job"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setJobs}
			ModalSize="xl"
		/>
	);
};

export default JobsPage;
