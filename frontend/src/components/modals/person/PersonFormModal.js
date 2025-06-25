import React, { useEffect, useState } from "react";
import { useAuth } from "../../../contexts/AuthContext";
import GenericModal from "../GenericModal";
import CompanyFormModal from "../company/CompanyFormModal";
import { formFields } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";
import { apiHelpers, companiesApi } from "../../../services/api";

export const PersonSwitchableModal = ({
	show,
	onHide,
	person,
	onSuccess,
	onDelete,
	endpoint = "persons",
	submode = "view",
	size = "lg",
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

	// Don't render if we're in view mode but have no person data
	if (submode === "view" && !person) {
		return null;
	}

	// Form fields for editing
	const formFieldsArray = [
		[formFields.firstName(), formFields.lastName()],
		[formFields.company(companyOptions, () => setShowCompanyModal(true)), formFields.role()],
		[formFields.email(), formFields.phone()],
		[formFields.linkedinUrl()],
	];

	// View fields for display
	const viewFieldsArray = [
		[viewFields.personName(), viewFields.linkedinUrl()],
		[viewFields.company(), viewFields.role()],
		[viewFields.email(), viewFields.phone()],
	];

	// Combine them in a way GenericModal can use based on mode
	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

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
				mode="formview"
				submode={submode}
				title="Person"
				size={size}
				data={person || {}} // Provide empty object instead of null
				fields={fields}
				endpoint={endpoint}
				onSuccess={onSuccess}
				onDelete={onDelete}
				validationRules={validationRules}
				transformFormData={transformFormData}
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

export const PersonFormModal = (props) => (
	<PersonSwitchableModal
		{...props}
		submode={props.person ? "edit" : "add"}
	/>
);

// Wrapper for view modal
export const PersonViewModal = (props) => (
	<PersonSwitchableModal
		{...props}
		submode="view"
	/>
);

// Add default export
export default PersonFormModal;