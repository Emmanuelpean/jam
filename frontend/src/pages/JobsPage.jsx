import React, { useEffect } from "react";
import { useTableData, GenericTableWithModals } from "../components/tables/GenericTable.tsx";
import { JobAndApplicationFormModal, JobAndApplicationViewModal } from "../components/modals/JobAndApplicationModal";
import { columns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext.tsx";

const JobsPage = () => {
	const { showLoading, hideLoading } = useLoading();
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
	} = useTableData("jobs", [], {}, { key: "created_at", direction: "desc" });

	console.log("JobsPage jobs:", jobs);

	// Use the global spinner instead of table spinner
	useEffect(() => {
		if (loading) {
			showLoading("Loading jobs...");
		} else {
			hideLoading();
		}

		// Cleanup function to hide loading when component unmounts
		return () => {
			hideLoading();
		};
	}, [loading, showLoading, hideLoading]);

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
			loading={false}
			error={error}
			FormModal={JobAndApplicationFormModal}
			ViewModal={JobAndApplicationViewModal}
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
