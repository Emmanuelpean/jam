import React, { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useTableData } from "../components/tables/Table";
import useGenericAlert from "../hooks/useGenericAlert";
import GenericTable, {
	createGenericDeleteHandler,
	createTableActions,
	displayNameFunctions,
} from "../components/tables/GenericTable";
import GenericModal from "../components/GenericModal";
import JobFormModal from "../components/modals/JobFormModal";
import JobViewModal from "../components/modals/JobViewModal";

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
		getItemDisplayName: displayNameFunctions.job,
		itemType: "Job",
	});

	// Define table columns (without actions)
	const columns = [
		{
			key: "title",
			label: "Job Title",
			sortable: true,
			searchable: true,
			type: "text",
		},
		{
			key: "company_name",
			label: "Company",
			sortable: true,
			searchable: true,
			type: "text",
			render: (job) => job.company_name || "Unknown",
		},
		{
			key: "location_name",
			label: "Location",
			sortable: true,
			searchable: true,
			type: "text",
			render: (job) => {
				if (!job.location_city) return "Unknown";
				return `${job.location_city}, ${job.location_country}${job.location_remote ? " (Remote)" : ""}`;
			},
		},
		{
			key: "status",
			label: "Status",
			sortable: true,
			searchable: true,
			type: "category",
			render: (job) => {
				const statusMap = {
					applied: "primary",
					interview: "warning",
					offer: "success",
					rejected: "danger",
					withdrawn: "secondary",
				};

				return (
					<span className={`badge bg-${statusMap[job.status] || "primary"}`}>
						{job.status.charAt(0).toUpperCase() + job.status.slice(1)}
					</span>
				);
			},
		},
		{
			key: "salary_min",
			label: "Salary Range",
			sortable: true,
			type: "number",
			render: (job) => {
				if (job.salary_min && job.salary_max) {
					return `$${Number(job.salary_min).toLocaleString()} - $${Number(job.salary_max).toLocaleString()}`;
				} else if (job.salary_min) {
					return `From $${Number(job.salary_min).toLocaleString()}`;
				} else if (job.salary_max) {
					return `Up to $${Number(job.salary_max).toLocaleString()}`;
				}
				return "Not specified";
			},
		},
		{
			key: "personal_rating",
			label: "Rating",
			sortable: true,
			type: "number",
			render: (job) => {
				const rating = job.personal_rating || 0;
				return (
					<div>
						{"★".repeat(rating)}
						{"☆".repeat(5 - rating)}
					</div>
				);
			},
		},
		{
			key: "created_at",
			label: "Date Applied",
			type: "date",
			sortable: true,
			render: (job) => new Date(job.created_at).toLocaleDateString(),
		},
	];

	// Create standardized actions using the utility function
	const tableActions = createTableActions([
		{ type: "view", onClick: handleView, title: "View job details" },
		{ type: "edit", onClick: handleEdit, title: "Edit job" },
		{ type: "delete", onClick: handleDelete, title: "Delete job" },
	]);

	const handleAddSuccess = (newJob) => {
		addItem(newJob);
	};

	return (
		<div className="container">
			<h2 className="my-4">Job Applications</h2>

			<GenericTable
				data={jobs}
				columns={columns}
				actions={tableActions}
				sortConfig={sortConfig}
				onSort={setSortConfig}
				searchTerm={searchTerm}
				onSearchChange={setSearchTerm}
				onAddClick={() => setShowModal(true)}
				addButtonText="Add Job"
				loading={loading}
				error={error}
				emptyMessage="No job applications found"
			/>

			{/* Modals */}
			<JobFormModal show={showModal} onHide={() => setShowModal(false)} onSuccess={handleAddSuccess} />

			<JobFormModal
				show={showEditModal}
				onHide={handleEditModalClose}
				onSuccess={handleEditSuccess}
				initialData={selectedJob || {}}
				isEdit={true}
			/>

			<JobViewModal
				show={showViewModal}
				onHide={() => setShowViewModal(false)}
				job={selectedJob}
				onEdit={handleEdit}
			/>

			{/* Alert Modal using GenericModal - handles both alerts and confirmations */}
			<GenericModal
				show={alertState.show}
				onHide={hideAlert}
				mode={alertState.cancelText ? "confirmation" : "alert"}
				title={alertState.title}
				alertMessage={alertState.message}
				confirmationMessage={alertState.message}
				alertType={alertState.type}
				confirmText={alertState.confirmText}
				cancelText={alertState.cancelText}
				alertIcon={alertState.icon}
				size={alertState.size}
				onSuccess={alertState.onSuccess}
				onConfirm={alertState.onSuccess}
			/>
		</div>
	);
};

export default JobsPage;
