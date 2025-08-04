import React, { useEffect, useState } from "react";
import { Badge, Button } from "react-bootstrap";
import { useAuth } from "../../../contexts/AuthContext";
import GenericModal from "../GenericModal";
import CompanyFormModal from "../CompanyModal";
import LocationFormModal from "../LocationModal";
import { KeywordFormModal } from "../KeywordModal";
import PersonFormModal from "../PersonModal";
import JobApplicationFormModal from "../job_application/JobApplicationFormModal";
import AlertModal from "../alert/AlertModal";
import useGenericAlert from "../../../hooks/useGenericAlert";
import { formFields } from "../../rendering/FormRenders";
import {
	apiHelpers,
	companiesApi,
	jobApplicationsApi,
	keywordsApi,
	locationsApi,
	personsApi,
} from "../../../services/api";
import { getApplicationStatusBadgeClass } from "../../rendering/Renders";

const JobFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false }) => {
	const { token } = useAuth();
	const { alertState, hideAlert, showDelete, showError } = useGenericAlert();
	const [showCompanyModal, setShowCompanyModal] = useState(false);
	const [showLocationModal, setShowLocationModal] = useState(false);
	const [showApplicationModal, setShowApplicationModal] = useState(false);
	const [showKeywordModal, setShowKeywordModal] = useState(false);
	const [showPersonModal, setShowPersonModal] = useState(false);

	const [companyOptions, setCompanyOptions] = useState([]);
	const [locationOptions, setLocationOptions] = useState([]);
	const [keywordOptions, setKeywordOptions] = useState([]);
	const [personOptions, setPersonOptions] = useState([]);
	const [currentJobId, setCurrentJobId] = useState(null);
	const [existingApplication, setExistingApplication] = useState(null);
	const [isLoadingApplication, setIsLoadingApplication] = useState(false);
	const [isDeleting, setIsDeleting] = useState(false);

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

	// Set current job ID when editing or after successful creation
	useEffect(() => {
		if (isEdit && initialData.id) {
			setCurrentJobId(initialData.id);
		}
	}, [isEdit, initialData.id]);

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

	// Fetch all options for the select fields
	useEffect(() => {
		const fetchOptions = async () => {
			if (!token || !show) return;

			try {
				const [companiesData, locationsData, keywordsData, personsData] = await Promise.all([
					companiesApi.getAll(token),
					locationsApi.getAll(token),
					keywordsApi.getAll(token),
					personsApi.getAll(token),
				]);

				setCompanyOptions(apiHelpers.toSelectOptions(companiesData));
				setLocationOptions(apiHelpers.toSelectOptions(locationsData));
				setKeywordOptions(apiHelpers.toSelectOptions(keywordsData));
				setPersonOptions(apiHelpers.toSelectOptions(personsData));
			} catch (error) {
				console.error("Error fetching options:", error);
			}
		};

		fetchOptions();
	}, [token, show]);

	// Success handlers for modals
	const handleCompanySuccess = (newCompany) => {
		const newOption = { value: newCompany.id, label: newCompany.name };
		setCompanyOptions((prev) => [...prev, newOption]);
		setShowCompanyModal(false);
	};

	const handleLocationSuccess = (newLocation) => {
		const newOption = { value: newLocation.id, label: newLocation.name };
		setLocationOptions((prev) => [...prev, newOption]);
		setShowLocationModal(false);
	};

	const handleKeywordSuccess = (newKeyword) => {
		const newOption = { value: newKeyword.id, label: newKeyword.name };
		setKeywordOptions((prev) => [...prev, newOption]);
		setShowKeywordModal(false);
	};

	const handlePersonSuccess = (newPerson) => {
		const newOption = { value: newPerson.id, label: newPerson.name };
		setPersonOptions((prev) => [...prev, newOption]);
		setShowPersonModal(false);
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

			setIsDeleting(true);
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
			} finally {
				setIsDeleting(false);
			}
		} catch (error) {
			console.log("Job application deletion cancelled");
		}
	};

	// Define form fields using new simplified structure
	const jobFields = [
		// Individual field
		formFields.jobTitle(),

		[
			formFields.company(companyOptions, () => setShowCompanyModal(true)),
			formFields.location(locationOptions, () => setShowLocationModal(true)),
		],

		[
			formFields.keywords(keywordOptions, () => setShowKeywordModal(true)),
			formFields.contacts(personOptions, () => setShowPersonModal(true)),
		],

		formFields.url({ label: "Job URL" }),

		[formFields.salaryMin(), formFields.salaryMax()],

		formFields.personalRating(),

		formFields.description(),
		formFields.note(),

		{
			type: "custom",
			content: (
				<div className="border-top pt-4 mt-4 mb-3">
					<div className="text-center">
						<div className="d-flex justify-content-center align-items-center mb-3">
							<h5 className="mb-0 me-3">
								<i className="bi bi-file-earmark-text me-2"></i>
								Job Application
							</h5>
							{existingApplication && (
								<Badge
									className={`${getApplicationStatusBadgeClass(existingApplication.status)} text-uppercase fw-bold`}
									style={{ fontSize: "1.25rem" }}
								>
									{existingApplication.status}
								</Badge>
							)}
							{isLoadingApplication && (
								<div className="spinner-border spinner-border-sm text-primary" role="status">
									<span className="visually-hidden">Loading...</span>
								</div>
							)}
						</div>

						{existingApplication ? (
							<>
								<p className="text-muted mb-3">
									Application submitted on {new Date(existingApplication.date).toLocaleDateString()}
								</p>
								<div className="d-grid gap-2 d-md-flex justify-content-md-center">
									<Button
										onClick={() => setShowApplicationModal(true)}
										className="px-4"
										style={{ width: "auto" }}
									>
										<i className="bi bi-pencil me-2"></i>
										Edit Application
									</Button>
									<Button
										variant="danger"
										onClick={handleDeleteApplication}
										disabled={isDeleting}
										className="px-4"
										style={{ width: "auto" }}
									>
										{isDeleting ? (
											<>
												<span
													className="spinner-border spinner-border-sm me-2"
													role="status"
													aria-hidden="true"
												></span>
												Deleting...
											</>
										) : (
											<>
												<i className="bi bi-trash me-2"></i>
												Delete Application
											</>
										)}
									</Button>
								</div>
							</>
						) : (
							<>
								<p className="text-muted mb-3">
									{currentJobId || isEdit
										? "Add an application for this job position"
										: "Save the job first, then you can add an application"}
								</p>
								<div className="d-grid gap-2 d-md-flex justify-content-md-center">
									<Button
										variant="success"
										size="lg"
										onClick={() => setShowApplicationModal(true)}
										disabled={!currentJobId && !isEdit}
										className="px-4"
									>
										<i className="bi bi-plus-circle me-2"></i>
										{currentJobId || isEdit ? "Create Job Application" : "Save Job First"}
									</Button>
								</div>
								{!currentJobId && !isEdit && (
									<small className="text-muted d-block mt-2">
										<i className="bi bi-info-circle me-1"></i>
										Complete and save this job form to enable application creation
									</small>
								)}
							</>
						)}
					</div>
				</div>
			),
		},
	];

	// Custom validation rules for job fields
	const validationRules = {
		salary_min: (value, formData) => {
			if (value && formData.salary_max && parseInt(value) > parseInt(formData.salary_max)) {
				return {
					isValid: false,
					message: "Minimum salary cannot be greater than maximum salary",
				};
			}
			return { isValid: true };
		},
		salary_max: (value, formData) => {
			if (value && formData.salary_min && parseInt(value) < parseInt(formData.salary_min)) {
				return {
					isValid: false,
					message: "Maximum salary cannot be less than minimum salary",
				};
			}
			return { isValid: true };
		},
	};

	// Transform form data before submission
	const transformFormData = (data) => {
		const transformed = { ...data };

		// Convert salary fields to integers if they exist
		if (transformed.salary_min) {
			transformed.salary_min = parseInt(transformed.salary_min);
		}
		if (transformed.salary_max) {
			transformed.salary_max = parseInt(transformed.salary_max);
		}

		// Convert personal_rating to integer
		if (transformed.personal_rating) {
			transformed.personal_rating = parseInt(transformed.personal_rating);
		}

		// Clean up unnecessary fields that shouldn't be sent to backend
		delete transformed.company;
		delete transformed.location;
		delete transformed.job_application;
		delete transformed.name;

		return transformed;
	};

	return (
		<>
			<GenericModal
				show={show}
				onHide={onHide}
				mode="form"
				title="Job"
				size={size}
				fields={jobFields}
				initialData={transformInitialData(initialData)}
				endpoint="jobs"
				onSuccess={handleJobSuccess}
				validationRules={validationRules}
				transformFormData={transformFormData}
				isEdit={isEdit}
			/>

			{/* Modals */}
			<CompanyFormModal
				show={showCompanyModal}
				onHide={() => setShowCompanyModal(false)}
				onSuccess={handleCompanySuccess}
			/>

			<LocationFormModal
				show={showLocationModal}
				onHide={() => setShowLocationModal(false)}
				onSuccess={handleLocationSuccess}
			/>

			<KeywordFormModal
				show={showKeywordModal}
				onHide={() => setShowKeywordModal(false)}
				onSuccess={handleKeywordSuccess}
			/>

			<PersonFormModal
				show={showPersonModal}
				onHide={() => setShowPersonModal(false)}
				onSuccess={handlePersonSuccess}
			/>

			<JobApplicationFormModal
				show={showApplicationModal}
				onHide={() => setShowApplicationModal(false)}
				onSuccess={handleApplicationSuccess}
				jobId={currentJobId || (isEdit ? initialData.id : null)}
				initialData={existingApplication || {}}
				isEdit={!!existingApplication}
				size="lg"
			/>

			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};

export default JobFormModal;
