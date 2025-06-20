import React, { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useTableData } from "../components/tables/Table";
import useGenericAlert from "../hooks/useGenericAlert";
import GenericTable, { createGenericDeleteHandler, createTableActions } from "../components/tables/GenericTable";
import JobFormModal from "../components/modals/JobFormModal";
import JobViewModal from "../components/modals/JobViewModal";
import AlertModal from "../components/AlertModal";
import { columns } from "../components/rendering/ColumnRenders";

const JobsPage = () => {
	const { token } = useAuth();
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

	const [showModal, setShowModal] = useState(false);
	const [showViewModal, setShowViewModal] = useState(false);
	const [showEditModal, setShowEditModal] = useState(false);
	const [selectedJob, setSelectedJob] = useState(null);

	const { alertState, showConfirm, showError, hideAlert } = useGenericAlert();

	// Handle view job
	const handleView = (job) => {
		setSelectedJob(job);
		setShowViewModal(true);
	};

	// Handle edit job
	const handleEdit = (job) => {
		setSelectedJob(job);
		setShowEditModal(true);
	};

	// Handle edit success
	const handleEditSuccess = (updatedJob) => {
		updateItem(updatedJob);
		setShowEditModal(false);
		setSelectedJob(null);
	};

	// Handle edit modal close
	const handleEditModalClose = () => {
		setShowEditModal(false);
		setSelectedJob(null);
	};

	// Create reusable delete handler using the generic function
	const handleDelete = createGenericDeleteHandler({
		endpoint: "jobs",
		token,
		showConfirm,
		showError,
		removeItem,
		setData: setJobs,
		nameKey: "title",
		itemType: "Job",
	});

	// Define table columns (without actions)
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

	// Create standardized actions using the utility function
	const tableActions = createTableActions([
		{ type: "view", onClick: handleView },
		{ type: "edit", onClick: handleEdit },
		{ type: "delete", onClick: handleDelete },
	]);

	const handleAddSuccess = (newJob) => {
		addItem(newJob);
	};

	return (
		<div className="container">
			<h2 className="my-4">Jobs</h2>

			<GenericTable
				data={jobs}
				columns={tableColumns}
				actions={tableActions}
				sortConfig={sortConfig}
				onSort={setSortConfig}
				searchTerm={searchTerm}
				onSearchChange={setSearchTerm}
				onAddClick={() => setShowModal(true)}
				addButtonText="Add Job"
				loading={loading}
				error={error}
				emptyMessage="No job found"
			/>

			{/* Modals */}
			<JobFormModal show={showModal} size="xl" onHide={() => setShowModal(false)} onSuccess={handleAddSuccess} />

			<JobFormModal
				show={showEditModal}
				onHide={handleEditModalClose}
				onSuccess={handleEditSuccess}
				initialData={selectedJob || {}}
				isEdit={true}
				size="xl"
			/>

			<JobViewModal
				show={showViewModal}
				onHide={() => setShowViewModal(false)}
				job={selectedJob}
				onEdit={handleEdit}
				size="xl"
			/>

			{/* Alert Modal using GenericModal - handles both alerts and confirmations */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</div>
	);
};

export default JobsPage;
