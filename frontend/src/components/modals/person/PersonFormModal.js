import { companiesApi, apiHelpers } from '../../../services/api';
import React, { useState, useEffect } from "react";
import { Button } from "react-bootstrap";
import { useAuth } from "../../../contexts/AuthContext";
import GenericModal from "../GenericModal";
import CompanyFormModal from "../company/CompanyFormModal";

const PersonFormModal = ({
							 show,
							 onHide,
							 onSuccess,
							 size,
							 initialData = {},
							 isEdit = false,
						 }) => {
	const { token } = useAuth();
	const [showCompanyModal, setShowCompanyModal] = useState(false);
	const [companyOptions, setCompanyOptions] = useState([]);

	useEffect(() => {
		const fetchCompanies = async () => {
			if (!token || !show) return;

			try {
				const companiesData = await companiesApi.getAll(token);
				setCompanyOptions(apiHelpers.toSelectOptions(companiesData));
			} catch (error) {
				console.error("Error fetching companies:", error);
			}
		};

		fetchCompanies();
	}, [token, show]);

	// Handle successful company creation
	const handleCompanyAddSuccess = (newCompany) => {
		const newOption = {
			value: newCompany.id,
			label: newCompany.name,
		};
		setCompanyOptions((prev) => [...prev, newOption]);
		setShowCompanyModal(false);
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
		// Company (full width) - Fixed structure
		{
			id: "company",
			type: "default",
			className: "mb-2",
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
					addButton: {
						onClick: () => setShowCompanyModal(true),
					},
				},
			],
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
					type: "text",
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

			{/* Company Add Modal */}
			<CompanyFormModal
				show={showCompanyModal}
				onHide={() => setShowCompanyModal(false)}
				onSuccess={handleCompanyAddSuccess}
				size="md"
			/>
		</>
	);
};

export default PersonFormModal;