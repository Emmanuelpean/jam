import { apiHelpers, companiesApi } from "../../../services/api";
import React, { useEffect, useState } from "react";
import { useAuth } from "../../../contexts/AuthContext";
import GenericModal from "../GenericModal";
import CompanyFormModal from "../company/CompanyFormModal";
import { formFields } from "../../rendering/FormRenders";

const PersonFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false }) => {
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

	const personFields = [
		[formFields.firstName(), formFields.lastName()],
		[formFields.company(companyOptions, () => setShowCompanyModal(true)), formFields.role()],
		[formFields.email(), formFields.phone()],
		[formFields.linkedinUrl()],
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
				fields={personFields}
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
