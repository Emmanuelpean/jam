import React from "react";
import GenericModal from "../GenericModal";

const KeywordFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false }) => {
	const formFields = [
		{
			name: "name",
			label: "Keyword Name",
			type: "text",
			required: true,
			placeholder: "Enter keyword name (e.g., Python, React, AWS)",
		},
	];

	// Custom validation to ensure keyword name is not empty after trimming
	const customValidation = (formData) => {
		const errors = {};

		if (!formData.name || !formData.name.trim()) {
			errors.name = "Keyword name is required";
		}

		return errors;
	};

	// Transform the form data before submission (trim whitespace)
	const transformFormData = (formData) => {
		return {
			...formData,
			name: formData.name ? formData.name.trim() : "",
		};
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="form"
			title="Keyword"
			fields={formFields}
			endpoint="keywords"
			onSuccess={onSuccess}
			initialData={initialData}
			isEdit={isEdit}
			customValidation={customValidation}
			transformFormData={transformFormData}
			size={size}
		/>
	);
};

export default KeywordFormModal;
