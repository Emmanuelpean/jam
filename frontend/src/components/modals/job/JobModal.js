import React, { useEffect, useMemo, useState } from "react";
import GenericModal from "../GenericModal";
import { formFields, useFormOptions } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";
import { useAuth } from "../../../contexts/AuthContext";
import useGenericAlert from "../../../hooks/useGenericAlert";
import { jobApplicationsApi } from "../../../services/api";
import JobApplicationFormModal from "../job_application/JobApplicationFormModal";

export const JobModal = ({
	show,
	onHide,
	job,
	onSuccess,
	onDelete,
	endpoint = "jobs",
	submode = "view",
	size = "lg",
}) => {
	const { token } = useAuth();
	const { showDelete, showError } = useGenericAlert();

	// Use the enhanced hook to get form options data and modal management
	const {
		companies,
		locations,
		keywords,
		persons,
		openCompanyModal,
		openLocationModal,
		openKeywordModal,
		openPersonModal,
		renderCompanyModal,
		renderLocationModal,
		renderKeywordModal,
		renderPersonModal,
	} = useFormOptions();

	const [currentJobId, setCurrentJobId] = useState(null);
	const [existingApplication, setExistingApplication] = useState(null);
	const [isLoadingApplication, setIsLoadingApplication] = useState(false);
	const [showApplicationModal, setShowApplicationModal] = useState(false);

	// Set current job ID when editing or viewing
	useEffect(() => {
		if (job?.id) {
			setCurrentJobId(job.id);
		}
	}, [job?.id]);

	// Check for existing job application
	const checkExistingApplication = async (jobId) => {
		if (!jobId || !token) return;

		setIsLoadingApplication(true);
		try {
			const applications = await jobApplicationsApi.getAll(token, { job_id: jobId });
			setExistingApplication(applications.length > 0 ? applications[0] : null);
		} catch (error) {
			console.error("Error fetching job applications:", error);
		} finally {
			setIsLoadingApplication(false);
		}
	};

	// Check for existing application when job ID changes
	useEffect(() => {
		if (currentJobId) {
			checkExistingApplication(currentJobId);
		}
	}, [currentJobId, token]);

	// Handle successful job application creation/update
	const handleApplicationSuccess = (applicationData) => {
		setShowApplicationModal(false);
		if (currentJobId) {
			checkExistingApplication(currentJobId);
		}
	};

	// Handle delete job application
	const handleDeleteApplication = async () => {
		if (!existingApplication?.id) return;

		try {
			await showDelete({
				title: "Delete Job Application",
				message: "Are you sure you want to delete this job application? This action cannot be undone.",
				confirmText: "Delete",
				cancelText: "Cancel",
			});

			try {
				await jobApplicationsApi.delete(existingApplication.id, token);
				setExistingApplication(null);
				console.log("Job application deleted successfully");
			} catch (error) {
				console.error("Error deleting job application:", error);
				showError({
					title: "Delete Failed",
					message: "Failed to delete job application. Please try again.",
				});
			}
		} catch (error) {
			console.log("Job application deletion cancelled");
		}
	};

	// Form fields for editing
	const formFieldsArray = useMemo(
		() => [
			formFields.jobTitle(),
			[formFields.company(companies, openCompanyModal), formFields.location(locations, openLocationModal)],
			[formFields.keywords(keywords, openKeywordModal), formFields.contacts(persons, openPersonModal)],
			formFields.url({ label: "Job URL" }),
			[formFields.salaryMin(), formFields.salaryMax()],
			formFields.personalRating(),
			formFields.description(),
			formFields.note(),
		],
		[
			companies,
			locations,
			keywords,
			persons,
			openCompanyModal,
			openLocationModal,
			openKeywordModal,
			openPersonModal,
		],
	);

	// View fields for display
	const viewFieldsArray = useMemo(
		() => [
			[viewFields.title(), viewFields.company()],
			[viewFields.location(), viewFields.jobApplication()],
			viewFields.description(),
			[viewFields.salaryRange(), viewFields.personalRating()],
			viewFields.url({ label: "Job URL" }),
			[viewFields.keywords(), viewFields.persons()],
		],
		[],
	);

	// Combine them in a way GenericModal can use based on mode
	const fields = useMemo(
		() => ({
			form: formFieldsArray,
			view: viewFieldsArray,
		}),
		[formFieldsArray, viewFieldsArray],
	);

	// Transform initial data to work with multiselect (convert objects to IDs)
	const transformInitialData = (data) => {
		if (!data) return data;

		const transformed = { ...data };

		// Convert keywords array to array of IDs
		if (transformed.keywords && Array.isArray(transformed.keywords)) {
			transformed.keywords = transformed.keywords.map((keyword) => {
				return typeof keyword === "object" ? keyword.id : keyword;
			});
		}

		// Convert contacts array to array of IDs
		if (transformed.contacts && Array.isArray(transformed.contacts)) {
			transformed.contacts = transformed.contacts.map((contact) => {
				return typeof contact === "object" ? contact.id : contact;
			});
		}

		return transformed;
	};

	// Transform form data before submission
	const transformFormData = (data) => {
		return {
			...data,
			title: data.title?.trim(),
			description: data.description?.trim() || null,
			note: data.note?.trim() || null,
			url: data.url?.trim() || null,
		};
	};

	// Handle successful job creation/update
	const handleJobSuccess = (jobData) => {
		if (jobData && jobData.id) {
			setCurrentJobId(jobData.id);
		}
		if (onSuccess) {
			onSuccess(jobData);
		}
	};

	// Don't render if we're in view mode but have no job data
	if (submode === "view" && !job?.id) {
		return null;
	}

	return (
		<>
			<GenericModal
				show={show}
				onHide={onHide}
				mode="formview"
				submode={submode}
				title="Job"
				size={size}
				data={transformInitialData(job || {})}
				fields={fields}
				endpoint={endpoint}
				onSuccess={handleJobSuccess}
				onDelete={onDelete}
				transformFormData={transformFormData}
			/>

			{/* Render all the sub-modals */}
			{renderCompanyModal()}
			{renderLocationModal()}
			{renderKeywordModal()}
			{renderPersonModal()}

			{/* Job Application Modal */}
			{showApplicationModal && (
				<JobApplicationFormModal
					show={showApplicationModal}
					onHide={() => setShowApplicationModal(false)}
					onSuccess={handleApplicationSuccess}
					initialData={{ job_id: currentJobId, ...existingApplication }}
					isEdit={!!existingApplication}
				/>
			)}
		</>
	);
};

export const JobFormModal = (props) => {
	// Determine the submode based on whether we have job data with an ID
	const submode = props.isEdit || props.job?.id ? "edit" : "add";
	return <JobModal {...props} submode={submode} />;
};

// Wrapper for view modal
export const JobViewModal = (props) => <JobModal {...props} submode="view" />;

// Add default export
export default JobFormModal;
