import React, { useState, useEffect } from "react";
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
		// Job Title (full width)
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
		// Company and Location (side by side)
		{
			id: "company-location",
			type: "row",
			className: "mb-0",
			fields: [
				{
					name: "company_id",
					label: "Company",
					type: "react-select",
					required: true,
					placeholder: "Select or search company...",
					isSearchable: true,
					isClearable: true,
					options: companyOptions,
					columnClass: "col-md-6",
				},
				{
					name: "location_id",
					label: "Location",
					type: "react-select",
					required: true,
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
					required: true,
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
