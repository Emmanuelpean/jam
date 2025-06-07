import React from "react";
import GenericFormModal from "../GenericModal";

const CompanyFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false }) => {
	// Define form fields for company
	const formFields = [
		{
			name: "name",
			label: "Company Name",
			type: "text",
			required: true,
			placeholder: "Enter company name",
		},
		{
			name: "url",
			label: "Website",
			type: "text",
			required: false,
			placeholder: "https://example.com",
		},
		{
			name: "description",
			label: "Description",
			type: "textarea",
			required: false,
			placeholder: "Enter company description",
		},
	];

	// Transform form data before submission
	const transformFormData = (formData) => {
		return {
			...formData,
			name: formData.name?.trim(),
			url: formData.url?.trim() || null,
			description: formData.description?.trim() || null,
		};
	};

	return (
		<GenericFormModal
			show={show}
			onHide={onHide}
			title="Company"
			fields={formFields}
			endpoint="companies"
			onSuccess={onSuccess}
			initialData={initialData}
			isEdit={isEdit}
			transformFormData={transformFormData}
			size={size}
		/>
	);
};

export default CompanyFormModal;
