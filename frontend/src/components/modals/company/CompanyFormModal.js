
import React from "react";
import GenericModal from "../GenericModal";
import { formFields } from "../../rendering/FormRenders";

const CompanyFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false }) => {

	const companyFields = [
		formFields.name({
			required: true,
		}),
		formFields.url({"label": "Website URL"}),
		formFields.description(),
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
		<GenericModal
			show={show}
			onHide={onHide}
			mode="form"
			title="Company"
			fields={companyFields}
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