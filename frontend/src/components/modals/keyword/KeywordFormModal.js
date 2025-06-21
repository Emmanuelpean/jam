import React from "react";
import GenericModal from "../GenericModal";
import { formFields } from "../../rendering/FormRenders";

const KeywordFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false }) => {

	const fields = [formFields.name()];

	// Transform the form data before submission (trim whitespace)
	const transformFormData = (formData) => {  // TODO create function that transforms the data based on the field type
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
			fields={fields}
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
