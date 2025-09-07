import React, { useEffect } from "react";
import { JobApplicationModal } from "../components/modals/JobApplicationModal";
import { GenericTableWithModals, useTableData } from "../components/tables/GenericTable";
import { tableColumns } from "../components/rendering/view/TableColumnRenders";
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
	} = useTableData("jobapplications", [], {}, { key: "date", direction: "desc" });

	const columns = [
		tableColumns.date!(),
		tableColumns.job!(),
		tableColumns.status!(),
		tableColumns.interviewCount!(),
		tableColumns.updateCount!(),
		tableColumns.url!({ label: "URL" }),
		tableColumns.createdAt!(),
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
			columns={columns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
			Modal={JobApplicationModal}
			endpoint="jobapplications"
			nameKey="title"
			itemType="Job Application"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setJobApplications}
			modalSize="xl"
		/>
	);
};

export default JobApplicationsPage;
