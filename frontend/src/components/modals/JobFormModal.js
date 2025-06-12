import React, { useEffect, useState } from "react";
import { Button, Badge } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import GenericModal from "../GenericModal";
import CompanyFormModal from "./CompanyFormModal";
import LocationFormModal from "./LocationFormModal";
import JobApplicationFormModal from "./JobApplicationFormModal";

const JobFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false }) => {
	const { token } = useAuth();
	const [showCompanyModal, setShowCompanyModal] = useState(false);
	const [showLocationModal, setShowLocationModal] = useState(false);
	const [showApplicationModal, setShowApplicationModal] = useState(false);
	const [companyOptions, setCompanyOptions] = useState([]);
	const [locationOptions, setLocationOptions] = useState([]);
	const [currentJobId, setCurrentJobId] = useState(null);
	const [existingApplication, setExistingApplication] = useState(null);
	const [isLoadingApplication, setIsLoadingApplication] = useState(false);

	// Set current job ID when editing or after successful creation
	useEffect(() => {
		if (isEdit && initialData.id) {
			setCurrentJobId(initialData.id);
		}
	}, [isEdit, initialData.id]);

	// Function to get application status badge class (from renders.js)
	const getApplicationStatusBadgeClass = (status) => {
		switch (status?.toLowerCase()) {
			case "applied":
				return "bg-primary";
			case "interview":
				return "bg-warning text-dark";
			case "offer":
				return "bg-success";
			case "rejected":
				return "bg-danger";
			case "withdrawn":
				return "bg-secondary";
			default:
				return "bg-light text-dark";
		}
	};

	// Check for existing job application
	const checkExistingApplication = async (jobId) => {
		if (!jobId || !token) return;

		setIsLoadingApplication(true);
		try {
			const response = await fetch("http://localhost:8000/jobapplications/", {
				headers: {
					Authorization: `Bearer ${token}`,
				},
			});

			if (response.ok) {
				const applications = await response.json();
				const existing = applications.find((app) => app.job_id === jobId);
				setExistingApplication(existing);
			}
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

	// Fetch companies and locations for the select options
	useEffect(() => {
		const fetchOptions = async () => {
			if (!token || !show) return;

			try {
				// Fetch companies
				const companiesResponse = await fetch("http://localhost:8000/companies/", {
					headers: {
						Authorization: `Bearer ${token}`,
					},
				});

				// Fetch locations
				const locationsResponse = await fetch("http://localhost:8000/locations/", {
					headers: {
						Authorization: `Bearer ${token}`,
					},
				});

				if (companiesResponse.ok && locationsResponse.ok) {
					const companiesData = await companiesResponse.json();
					const locationsData = await locationsResponse.json();

					setCompanyOptions(
						companiesData.map((company) => ({
							value: company.id,
							label: company.name,
						})),
					);

					setLocationOptions(
						locationsData.map((location) => ({
							value: location.id,
							label: `${location.city}, ${location.country}${location.remote ? " (Remote)" : ""}`,
						})),
					);
				}
			} catch (error) {
				console.error("Error fetching options:", error);
			}
		};

		fetchOptions();
	}, [token, show]);

	// Handle successful company creation
	const handleCompanySuccess = (newCompany) => {
		const newOption = {
			value: newCompany.id,
			label: newCompany.name,
		};
		setCompanyOptions((prev) => [...prev, newOption]);
		setShowCompanyModal(false);
	};

	// Handle successful location creation
	const handleLocationSuccess = (newLocation) => {
		const newOption = {
			value: newLocation.id,
			label: `${newLocation.city}, ${newLocation.country}${newLocation.remote ? " (Remote)" : ""}`,
		};
		setLocationOptions((prev) => [...prev, newOption]);
		setShowLocationModal(false);
	};

	// Handle successful job creation/update
	const handleJobSuccess = (jobData) => {
		// Store the job ID for potential application creation
		if (jobData && jobData.id) {
			setCurrentJobId(jobData.id);
		}
		// Call the original onSuccess callback
		if (onSuccess) {
			onSuccess(jobData);
		}
	};

	// Handle successful job application creation/update
	const handleApplicationSuccess = (applicationData) => {
		setShowApplicationModal(false);
		// Refresh the existing application data
		if (currentJobId) {
			checkExistingApplication(currentJobId);
		}
		console.log("Job application created/updated successfully:", applicationData);
	};

	// Handle opening application modal (create or edit)
	const handleOpenApplicationModal = () => {
		setShowApplicationModal(true);
	};

	// Define layout groups for job information only
	const layoutGroups = [
		{
			id: "title",
			type: "default",
			fields: [
				{
					name: "title",
					label: "Job Title",
					type: "text",
					required: true,
					placeholder: "Enter job title",
				},
			],
		},
		{
			id: "company-location",
			type: "row",
			className: "mb-0",
			fields: [
				{
					name: "company_id",
					label: "Company",
					type: "select",
					placeholder: "Select or search company...",
					isSearchable: true,
					isClearable: true,
					options: companyOptions,
					columnClass: "col-md-6",
				},
				{
					name: "location_id",
					label: "Location",
					type: "select",
					placeholder: "Select or search location...",
					isSearchable: true,
					isClearable: true,
					options: locationOptions,
					columnClass: "col-md-6",
				},
			],
		},
		// Add New buttons (side by side)
		{
			id: "add-buttons",
			type: "custom",
			className: "mb-3",
			content: (
				<div className="row">
					<div className="col-md-6">
						<div className="d-grid">
							<Button variant="outline-primary" size="sm" onClick={() => setShowCompanyModal(true)}>
								<i className="bi bi-plus-circle me-2"></i>
								Add New Company
							</Button>
						</div>
					</div>
					<div className="col-md-6">
						<div className="d-grid">
							<Button variant="outline-primary" size="sm" onClick={() => setShowLocationModal(true)}>
								<i className="bi bi-plus-circle me-2"></i>
								Add New Location
							</Button>
						</div>
					</div>
				</div>
			),
		},
		// Status and URL (side by side)
		{
			id: "status-url",
			type: "default",
			fields: [
				{
					name: "url",
					label: "Job URL",
					type: "url",
					placeholder: "https://...",
				},
			],
		},
		// Salary fields (side by side)
		{
			id: "salary",
			type: "row",
			fields: [
				{
					name: "salary_min",
					label: "Minimum Salary",
					type: "number",
					placeholder: "Enter minimum salary",
					step: "1000",
					columnClass: "col-md-6",
				},
				{
					name: "salary_max",
					label: "Maximum Salary",
					type: "number",
					placeholder: "Enter maximum salary",
					step: "1000",
					columnClass: "col-md-6",
				},
			],
		},
		// Personal Rating (full width)
		{
			id: "rating",
			type: "default",
			fields: [
				{
					name: "personal_rating",
					label: "Personal Rating (1-5)",
					type: "select",
					options: [
						{ value: 1, label: "1 - Poor" },
						{ value: 2, label: "2 - Fair" },
						{ value: 3, label: "3 - Good" },
						{ value: 4, label: "4 - Very Good" },
						{ value: 5, label: "5 - Excellent" },
					],
				},
			],
		},
		// Description and Notes (full width)
		{
			id: "text-fields",
			type: "default",
			fields: [
				{
					name: "description",
					label: "Job Description",
					type: "textarea",
					rows: 4,
					placeholder: "Enter job description...",
				},
				{
					name: "notes",
					label: "Personal Notes",
					type: "textarea",
					rows: 3,
					placeholder: "Add your notes about this job...",
				},
			],
		},
		// Job Application Section
		{
			id: "application-section",
			type: "custom",
			className: "mt-4 mb-3",
			content: (
				<div className="border-top pt-4">
					<div className="text-center">
						<div className="d-flex justify-content-center align-items-center mb-3">
							<h5 className="mb-0 me-3">
								<i className="bi bi-file-earmark-text me-2"></i>
								Job Application
							</h5>
							{existingApplication && (
								<Badge
									className={`${getApplicationStatusBadgeClass(existingApplication.status)} text-uppercase fw-bold`}
									style={{ fontSize: "0.75rem" }}
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
										variant="outline-primary"
										size="lg"
										onClick={handleOpenApplicationModal}
										className="px-4"
									>
										<i className="bi bi-pencil me-2"></i>
										Edit Application
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
										onClick={handleOpenApplicationModal}
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

	// Custom validation rules for job fields only
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

	// Transform form data before submission (job fields only)
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

		// Set default status if not provided
		if (!transformed.status) {
			transformed.status = "applied";
		}

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
				useCustomLayout={true}
				layoutGroups={layoutGroups}
				initialData={initialData}
				endpoint="jobs"
				onSuccess={handleJobSuccess}
				validationRules={validationRules}
				transformFormData={transformFormData}
				isEdit={isEdit}
			/>

			{/* Company Form Modal */}
			<CompanyFormModal
				show={showCompanyModal}
				onHide={() => setShowCompanyModal(false)}
				onSuccess={handleCompanySuccess}
			/>

			{/* Location Form Modal */}
			<LocationFormModal
				show={showLocationModal}
				onHide={() => setShowLocationModal(false)}
				onSuccess={handleLocationSuccess}
			/>

			{/* Job Application Form Modal */}
			<JobApplicationFormModal
				show={showApplicationModal}
				onHide={() => setShowApplicationModal(false)}
				onSuccess={handleApplicationSuccess}
				jobId={currentJobId || (isEdit ? initialData.id : null)}
				initialData={existingApplication || {}}
				isEdit={!!existingApplication}
				size="lg"
			/>
		</>
	);
};

export default JobFormModal;
