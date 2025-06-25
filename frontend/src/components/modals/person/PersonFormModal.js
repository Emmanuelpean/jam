import React from "react";
import GenericModal from "../GenericModal";
import { formFields, useFormOptions } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";

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
	// Use the enhanced hook to get form options data and modal management
	const { companies, openCompanyModal, renderCompanyModal } = useFormOptions();

	// Don't render if we're in view mode but have no person data
	if (submode === "view" && !person?.id) {
		return null;
	}

	// Form fields for editing - using the static formFields with companies data and add button
	const formFieldsArray = [
		[formFields.firstName(), formFields.lastName()],
		[formFields.company(companies, openCompanyModal), formFields.role()],
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
				data={person || {}}
				fields={fields}
				endpoint={endpoint}
				onSuccess={onSuccess}
				onDelete={onDelete}
				validationRules={validationRules}
				transformFormData={transformFormData}
			/>

			{renderCompanyModal()}
		</>
	);
};

export const PersonFormModal = (props) => {
	// Determine the submode based on whether we have person data with an ID
	const submode = props.isEdit || props.person?.id ? "edit" : "add";
	return <PersonSwitchableModal {...props} submode={submode} />;
};

// Wrapper for view modal
export const PersonViewModal = (props) => <PersonSwitchableModal {...props} submode="view" />;

// Add default export
export default PersonFormModal;
