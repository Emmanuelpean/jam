import React, { useState, useEffect } from "react";
import { Button, ButtonGroup } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import GenericModal from "../GenericModal";
import CompanyFormModal from "./CompanyFormModal";
import CompanyViewModal from "./CompanyViewModal";
import useGenericAlert from "../../hooks/useGenericAlert";
import AlertModal from "../AlertModal";

const PersonFormModal = ({
	show,
	onHide,
	onSuccess,
	size,
	initialData = {},
	isEdit = false,
	// Company handling props - passed from parent
	companyOptions = [],
	onCompanyAdd = null,
	onCompanyEdit = null,
	onCompanyView = null,
	onCompanyDelete = null,
	refreshCompanies = null,
}) => {
	const { token } = useAuth();
	const [showCompanyModal, setShowCompanyModal] = useState(false);
	const [selectedCompany, setSelectedCompany] = useState(null);

	const { alertState, showConfirm, showError, hideAlert } = useGenericAlert();

	// Update selected company when company_id changes
	useEffect(() => {
		if (initialData?.company_id) {
			const company = companyOptions.find((opt) => opt.value === initialData.company_id);
			setSelectedCompany(company || null);
		}
	}, [initialData?.company_id, companyOptions]);

	// Handle successful company creation
	const handleCompanyAddSuccess = (newCompany) => {
		// Call parent's add handler if available
		if (onCompanyAdd) {
			onCompanyAdd(newCompany);
		}

		// Select the new company
		const newOption = {
			value: newCompany.id,
			label: newCompany.name,
			...newCompany,
		};
		setSelectedCompany(newOption);
		setShowCompanyModal(false);
	};

	// Company action handlers - delegate to parent functions
	const handleViewCompany = (company) => {
		if (onCompanyView) {
			onCompanyView(company);
		}
	};

	const handleEditCompany = (company) => {
		if (onCompanyEdit) {
			onCompanyEdit(company);
		}
	};

	const handleDeleteCompany = async (company) => {
		if (onCompanyDelete) {
			await onCompanyDelete(company);
			// Clear selection if deleted company was selected
			if (selectedCompany?.value === company.value) {
				setSelectedCompany(null);
			}
			// Refresh companies list
			if (refreshCompanies) {
				refreshCompanies();
			}
		}
	};

	// Handle company selection change
	const handleCompanyChange = (selectedOption) => {
		setSelectedCompany(selectedOption);
	};

	// Define layout groups for custom form layout
	const layoutGroups = [
		// Name fields (side by side)
		{
			id: "name",
			type: "row",
			fields: [
				{
					name: "first_name",
					label: "First Name",
					type: "text",
					required: true,
					placeholder: "Enter first name",
					columnClass: "col-md-6",
				},
				{
					name: "last_name",
					label: "Last Name",
					type: "text",
					required: true,
					placeholder: "Enter last name",
					columnClass: "col-md-6",
				},
			],
		},
		// Company (full width)
		{
			id: "company",
			type: "default",
			className: "mb-0",
			fields: [
				{
					name: "company_id",
					label: "Company",
					type: "select",
					required: true,
					placeholder: "Select or search company...",
					isSearchable: true,
					isClearable: true,
					options: companyOptions,
					onChange: handleCompanyChange,
				},
			],
		},
		// Company action buttons
		{
			id: "company-actions",
			type: "custom",
			className: "mb-3",
			content: (
				<ButtonGroup size="sm" className="w-100">
					<Button
						variant="outline-secondary"
						onClick={() => setShowCompanyModal(true)}
						title="Add new company"
					>
						<i className="bi bi-plus-circle me-1"></i>
						Add New
					</Button>

					{selectedCompany && (
						<>
							<Button
								variant="outline-secondary"
								onClick={() => handleViewCompany(selectedCompany)}
								title="View company details"
								disabled={!onCompanyView}
							>
								<i className="bi bi-eye me-1"></i>
								View
							</Button>
							<Button
								variant="outline-secondary"
								onClick={() => handleEditCompany(selectedCompany)}
								title="Edit company"
								disabled={!onCompanyEdit}
							>
								<i className="bi bi-pencil me-1"></i>
								Edit
							</Button>
							<Button
								variant="outline-secondary"
								onClick={() => handleDeleteCompany(selectedCompany)}
								title="Delete company"
								disabled={!onCompanyDelete}
							>
								<i className="bi bi-trash me-1"></i>
								Delete
							</Button>
						</>
					)}
				</ButtonGroup>
			),
		},
		// Contact fields (side by side)
		{
			id: "contact",
			type: "row",
			fields: [
				{
					name: "email",
					label: "Email",
					type: "email",
					required: false,
					placeholder: "person@company.com",
					columnClass: "col-md-6",
				},
				{
					name: "phone",
					label: "Phone",
					type: "tel",
					required: false,
					placeholder: "+1-555-0123",
					columnClass: "col-md-6",
				},
			],
		},
		// LinkedIn URL (full width)
		{
			id: "linkedin",
			type: "default",
			fields: [
				{
					name: "linkedin_url",
					label: "LinkedIn Profile",
					type: "url",
					required: false,
					placeholder: "https://linkedin.com/in/username",
				},
			],
		},
	];

	// Custom validation rules
	const validationRules = {
		email: (value) => {
			if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
				return {
					isValid: false,
					message: "Please enter a valid email address",
				};
			}
			return { isValid: true };
		},
		linkedin_url: (value) => {
			if (value && !value.includes("linkedin.com")) {
				return {
					isValid: false,
					message: "Please enter a valid LinkedIn URL",
				};
			}
			return { isValid: true };
		},
	};

	// Transform form data before submission
	const transformFormData = (data) => {
		return {
			...data,
			first_name: data.first_name?.trim(),
			last_name: data.last_name?.trim(),
			email: data.email?.trim() || null,
			phone: data.phone?.trim() || null,
			linkedin_url: data.linkedin_url?.trim() || null,
		};
	};

	return (
		<>
			<GenericModal
				show={show}
				onHide={onHide}
				mode="form"
				title="Person"
				size={size}
				useCustomLayout={true}
				backdrop={true}
				layoutGroups={layoutGroups}
				initialData={initialData}
				endpoint="persons"
				onSuccess={onSuccess}
				validationRules={validationRules}
				transformFormData={transformFormData}
				isEdit={isEdit}
			/>

			{/* Company Add Modal - only this one is managed locally */}
			<CompanyFormModal
				show={showCompanyModal}
				onHide={() => setShowCompanyModal(false)}
				onSuccess={handleCompanyAddSuccess}
				size="md"
			/>

			{/* Alert Modal for local confirmations and errors */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};

export default PersonFormModal;
