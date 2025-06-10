import React from "react";
import GenericModal from "../GenericModal";
import renderInputField from "../formFieldRender";

const KeywordFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false }) => {
	const formFields = [
		{
			name: "name",
			label: "Tag Name",
			type: "text",
			required: true,
			placeholder: "Enter tag name (e.g., Python, React, AWS)",
		},
	];

	// Transform the form data before submission (trim whitespace)
	const transformFormData = (formData) => {
		return {
			...formData,
			name: formData.name.trim(),
		};
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="form"
			title="Tag"
			fields={formFields}
			endpoint="keywords"
			onSuccess={onSuccess}
			initialData={initialData}
			isEdit={isEdit}
			transformFormData={transformFormData}
			size={size}
		/>
	);
};

export default KeywordFormModal;
