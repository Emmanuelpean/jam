import React, { useEffect } from "react";
import { useTableData, GenericTableWithModals } from "../components/tables/GenericTable";
import { JobAndApplicationModal } from "../components/modals/JobAndApplicationModal";
import { tableColumns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext";

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

	const columns = [
		tableColumns.title!(),
		tableColumns.company!(),
		tableColumns.location!(),
		tableColumns.urlGeneric!(),
		tableColumns.salaryRange!(),
		tableColumns.personalRating!(),
		tableColumns.status!(),
		tableColumns.createdAt!(),
	];

	return (
		<GenericTableWithModals
			title="Jobs"
			data={jobs}
			columns={columns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
			Modal={JobAndApplicationModal}
			endpoint="jobs"
			nameKey="title"
			itemType="Job"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setJobs}
			modalSize="xl"
		/>
	);
};

export default JobsPage;
