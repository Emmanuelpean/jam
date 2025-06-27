import React from "react";
import GenericModal from "../GenericModal";
import { formFields } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";

export const CompanyModal = ({
	show,
	onHide,
	company,
	onSuccess,
	onDelete,
	endpoint = "companies",
	submode = "view",
	size = "lg",
}) => {
	// Don't render if we're in view mode but have no company data
	if (submode === "view" && !company?.id) {
		return null;
	}

	// Form fields for editing
	const formFieldsArray = [
		[formFields.name({ required: true })],
		[formFields.url({ label: "Website URL" })],
		[formFields.description()],
	];

	// View fields for display
	const viewFieldsArray = [[viewFields.name(), viewFields.url()], [viewFields.description()]];

	// Combine them in a way GenericModal can use based on mode
	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	// Custom validation rules
	const validationRules = {
		url: (value) => {
			if (value && !/^https?:\/\/.+/.test(value)) {
				return {
					isValid: false,
					message: "Please enter a valid URL (starting with http:// or https://)",
				};
			}
			return { isValid: true };
		},
	};

	// Transform form data before submission
	const transformFormData = (data) => {
		return {
			...data,
			name: data.name?.trim(),
			url: data.url?.trim() || null,
			description: data.description?.trim() || null,
		};
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="formview"
			submode={submode}
			title="Company"
			size={size}
			data={company || {}}
			fields={fields}
			endpoint={endpoint}
			onSuccess={onSuccess}
			onDelete={onDelete}
			validationRules={validationRules}
			transformFormData={transformFormData}
		/>
	);
};

export const CompanyFormModal = (props) => {
	// Determine the submode based on whether we have company data with an ID
	const submode = props.isEdit || props.company?.id ? "edit" : "add";
	return <CompanyModal {...props} submode={submode} />;
};

// Wrapper for view modal
export const CompanyViewModal = (props) => <CompanyModal {...props} submode="view" />;

// Add default export
export default CompanyFormModal;
