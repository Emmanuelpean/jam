import React, { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useTableData } from "../components/tables/Table";
import useGenericAlert from "../hooks/useGenericAlert";
import GenericTable, { createGenericDeleteHandler, createTableActions } from "../components/tables/GenericTable";
import GenericModal from "../components/GenericModal";
import JobFormModal from "../components/modals/JobFormModal";
import JobViewModal from "../components/modals/JobViewModal";
import AlertModal from "../components/AlertModal";

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
		getItemDisplayName: (job) => job.title || `job #${job.id}`,
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
			// render: (job) => job.company.name || "/",
		},
		{
			key: "location_name",
			label: "Location",
			sortable: true,
			searchable: true,
			type: "text",
			render: (job) => {
				if (!job.location_city) return "/";
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

				// Add null check and type check before calling charAt
				const status = job.status && typeof job.status === "string" ? job.status : "unknown";
				const statusText = status.charAt(0).toUpperCase() + status.slice(1);

				return <span className={`badge bg-${statusMap[job.status] || "primary"}`}>{statusText}</span>;
			},
		},
		{
			key: "salary_min",
			label: "Salary",
			sortable: true,
			type: "number",
			render: (job) => {
				if (job.salary_min && job.salary_max) {
					// Check if min and max are the same
					if (job.salary_min === job.salary_max) {
						return `£${Number(job.salary_min).toLocaleString()}`;
					}
					return `£${Number(job.salary_min).toLocaleString()} - £${Number(job.salary_max).toLocaleString()}`;
				} else if (job.salary_min) {
					return `From £${Number(job.salary_min).toLocaleString()}`;
				} else if (job.salary_max) {
					return `Up to £${Number(job.salary_max).toLocaleString()}`;
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
				// Check if rating is null or undefined
				if (job.personal_rating === null || job.personal_rating === undefined) {
					return "/";
				}

				const rating = Math.max(0, Math.min(5, job.personal_rating)); // Clamp between 0 and 5
				const filledStars = Math.floor(rating);
				const emptyStars = 5 - filledStars;

				return (
					<div>
						{"★".repeat(filledStars)}
						{"☆".repeat(emptyStars)}
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
