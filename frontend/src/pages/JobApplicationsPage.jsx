import React, { useEffect } from "react";
import { JobApplicationModal } from "../components/modals/JobApplicationModal";
import { GenericTableWithModals, useTableData } from "../components/tables/GenericTable.tsx";
import { columns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext.tsx";

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

	const tableColumns = [
		columns.date(),
		columns.job(),
		columns.status(),
		columns.interviewCount(),
		columns.updateCount(),
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
			Modal={JobApplicationModal}
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
