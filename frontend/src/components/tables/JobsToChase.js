import React, { useState, useEffect } from "react";
import { Alert } from "react-bootstrap";
import { GenericTableWithModals } from "./TableSystem";
import { columns } from "../rendering/ColumnRenders";
import { JobViewModal } from "../modals/job/JobModal";

const JobsToChase = ({ initialData = [], onDataChange, loading: externalLoading = false }) => {
	const [jobsToChase, setJobsToChase] = useState(initialData);
	const [sortConfig, setSortConfig] = useState({ key: "created_at", direction: "desc" });
	const [searchTerm, setSearchTerm] = useState("");

	// Update local data when initialData changes
	useEffect(() => {
		setJobsToChase(initialData);
	}, [initialData]);

	// Notify parent component when data changes
	const handleDataChange = (newData) => {
		setJobsToChase(newData);
		if (onDataChange) {
			onDataChange(newData);
		}
	};

	const tableColumns = [
		columns.title(),
		columns.company(),
		columns.location(),
		columns.daysSinceLastUpdate(),
		columns.lastUpdateType(),
	];

	// Handle success for combined modal updates
	const handleJobSuccess = (updatedJob) => {
		const updatedData = jobsToChase.map((job) => (job.id === updatedJob.id ? updatedJob : job));
		handleDataChange(updatedData);
	};

	const handleJobApplicationSuccess = (updatedApplication) => {
		// Find the corresponding job and update it
		const jobIndex = jobsToChase.findIndex((job) => job.job_application?.id === updatedApplication.id);
		if (jobIndex !== -1) {
			const updatedJob = {
				...jobsToChase[jobIndex],
				job_application: updatedApplication,
			};
			const updatedData = [...jobsToChase];
			updatedData[jobIndex] = updatedJob;
			handleDataChange(updatedData);
		}
	};

	const addItem = (newItem) => {
		const updatedData = [newItem, ...jobsToChase];
		handleDataChange(updatedData);
	};

	const updateItem = (updatedItem) => {
		const updatedData = jobsToChase.map((item) => (item.id === updatedItem.id ? updatedItem : item));
		handleDataChange(updatedData);
	};

	const removeItem = (itemId) => {
		const updatedData = jobsToChase.filter((item) => item.id !== itemId);
		handleDataChange(updatedData);
	};

	// Custom modal wrapper to handle both job and application data
	const ChaseJobModal = (props) => {
		const jobData = props.data;
		const applicationData = jobData?.job_application;

		return (
			<JobViewModal
				{...props}
				jobData={jobData}
				jobApplicationData={applicationData}
				jobSubmode="view"
				jobApplicationSubmode="edit" // Allow editing application to add updates
				defaultTab="application" // Start with application tab since that's what needs updating
				onJobSuccess={handleJobSuccess}
				onJobApplicationSuccess={handleJobApplicationSuccess}
			/>
		);
	};

	return (
		<div>
			<Alert variant="info" className="mb-4">
				<div className="d-flex align-items-center">
					<i className="bi bi-info-circle me-2"></i>
					<div>
						<strong>Jobs Requiring Follow-up</strong>
						<div className="small">
							These are jobs you've applied to that haven't had any updates in the past 30 days. Consider
							following up with the company or updating the application status.
						</div>
					</div>
				</div>
			</Alert>

			<GenericTableWithModals
				title="Jobs to Chase"
				data={jobsToChase}
				columns={tableColumns}
				sortConfig={sortConfig}
				onSort={setSortConfig}
				searchTerm={searchTerm}
				onSearchChange={setSearchTerm}
				loading={externalLoading}
				error={null}
				ViewModal={ChaseJobModal}
				FormModal={ChaseJobModal}
				endpoint="jobs"
				nameKey="title"
				itemType="Job"
				addItem={addItem}
				updateItem={updateItem}
				removeItem={removeItem}
				setData={handleDataChange}
				ModalSize="xl"
				emptyMessage={
					<div className="text-center py-5">
						<i className="bi bi-check-circle text-success" style={{ fontSize: "3rem" }}></i>
						<h4 className="mt-3">Great job!</h4>
						<p className="text-muted">
							No applications need follow-up at this time. All your applications have been updated
							recently.
						</p>
					</div>
				}
			/>
		</div>
	);
};

export default JobsToChase;
