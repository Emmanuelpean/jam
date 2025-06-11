import React, { useEffect, useState } from "react";
import { Button } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import GenericModal from "../GenericModal";
import CompanyFormModal from "./CompanyFormModal";
import LocationFormModal from "./LocationFormModal";

const JobFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false }) => {
	const { token } = useAuth();
	const [showCompanyModal, setShowCompanyModal] = useState(false);
	const [showLocationModal, setShowLocationModal] = useState(false);
	const [companyOptions, setCompanyOptions] = useState([]);
	const [locationOptions, setLocationOptions] = useState([]);

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

	// Define layout groups for custom form layout
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
			type: "row",
			fields: [
				{
					name: "status",
					label: "Status",
					type: "select",
					options: [
						{ value: "applied", label: "Applied" },
						{ value: "interview", label: "Interview" },
						{ value: "offer", label: "Offer" },
						{ value: "rejected", label: "Rejected" },
						{ value: "withdrawn", label: "Withdrawn" },
					],
					columnClass: "col-md-6",
				},
				{
					name: "url",
					label: "Job URL",
					type: "url",
					placeholder: "https://...",
					columnClass: "col-md-6",
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
		// Job Application Fields Section
		{
			id: "application-header",
			type: "custom",
			className: "mt-4 mb-3",
			content: (
				<div className="border-top pt-3">
					<h5 className="mb-0">
						<i className="bi bi-file-earmark-text me-2"></i>
						Application Details
					</h5>
					<small className="text-muted">Track your application progress and files</small>
				</div>
			),
		},
		// Application Date and Status
		{
			id: "application-date-status",
			type: "row",
			fields: [
				{
					name: "application_date",
					label: "Application Date",
					type: "datetime-local",
					placeholder: "Select application date and time",
					columnClass: "col-md-6",
				},
				{
					name: "application_status",
					label: "Application Status",
					type: "select",
					options: [
						{ value: "Applied", label: "Applied" },
						{ value: "Interview", label: "Interview" },
						{ value: "Rejected", label: "Rejected" },
						{ value: "Offer", label: "Offer" },
						{ value: "Withdrawn", label: "Withdrawn" },
					],
					defaultValue: "Applied",
					columnClass: "col-md-6",
				},
			],
		},
		// Application URL
		{
			id: "application-url",
			type: "default",
			fields: [
				{
					name: "application_url",
					label: "Application URL",
					type: "url",
					placeholder: "https://... (link to your application submission)",
				},
			],
		},
		// Application Note
		{
			id: "application-note",
			type: "default",
			fields: [
				{
					name: "application_note",
					label: "Application Notes",
					type: "textarea",
					rows: 3,
					placeholder: "Add notes about your application process, interview details, etc...",
				},
			],
		},
		// File Uploads Section
		{
			id: "files-header",
			type: "custom",
			className: "mt-4 mb-3",
			content: (
				<div className="border-top pt-3">
					<h6 className="mb-0">
						<i className="bi bi-paperclip me-2"></i>
						Application Documents
					</h6>
					<small className="text-muted">Upload your CV and cover letter</small>
				</div>
			),
		},
		// File uploads (side by side)
		{
			id: "application-files",
			type: "row",
			fields: [
				{
					name: "cv",
					label: "CV/Resume",
					type: "file",
					accept: ".pdf,.doc,.docx",
					placeholder: "Upload your CV or resume",
					columnClass: "col-md-6",
				},
				{
					name: "cover_letter",
					label: "Cover Letter",
					type: "file",
					accept: ".pdf,.doc,.docx",
					placeholder: "Upload your cover letter",
					columnClass: "col-md-6",
				},
			],
		},
	];

	// Custom validation rules
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
		application_date: (value) => {
			if (value) {
				const selectedDate = new Date(value);
				const now = new Date();
				if (selectedDate > now) {
					return {
						isValid: false,
						message: "Application date cannot be in the future",
					};
				}
			}
			return { isValid: true };
		},
		cv: (value) => {
			if (value && value.size > 10 * 1024 * 1024) { // 10MB limit
				return {
					isValid: false,
					message: "CV file size must be less than 10MB",
				};
			}
			return { isValid: true };
		},
		cover_letter: (value) => {
			if (value && value.size > 10 * 1024 * 1024) { // 10MB limit
				return {
					isValid: false,
					message: "Cover letter file size must be less than 10MB",
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

		// Set default status if not provided
		if (!transformed.status) {
			transformed.status = "applied";
		}

		// Handle job application data - only include if application_date is set
		if (transformed.application_date) {
			// Convert to ISO string for backend
			transformed.application_date = new Date(transformed.application_date).toISOString();

			// Set default application status to "Applied" if not provided
			if (!transformed.application_status) {
				transformed.application_status = "Applied";
			}

			// Include application fields only when application_date is provided
			transformed.job_application = {
				date: transformed.application_date,
				status: transformed.application_status,
				url: transformed.application_url?.trim() || null,
				note: transformed.application_note?.trim() || null,
				// Files will be handled separately by the form submission
				cv: transformed.cv || null,
				cover_letter: transformed.cover_letter || null,
			};
		}

		// Remove the individual application fields from the main object
		// since they're now nested in job_application
		delete transformed.application_date;
		delete transformed.application_status;
		delete transformed.application_url;
		delete transformed.application_note;
		delete transformed.cv;
		delete transformed.cover_letter;

		return transformed;
	};


	return (
		<>
			<GenericModal
				show={show}
				onHide={onHide}
				mode="form"
				title="Job Application"
				size={size}
				useCustomLayout={true}
				layoutGroups={layoutGroups}
				initialData={initialData}
				endpoint="jobs"
				onSuccess={onSuccess}
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
		</>
	);
};

export default JobFormModal;
