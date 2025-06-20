import React from "react";
import GenericModal from "../GenericModal";

const AggregatorFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false }) => {

	const formFields = [
		{
			name: "name",
			label: "Aggregator Name",
			type: "text",
			required: true,
			placeholder: "Enter aggregator name (e.g., LinkedIn, Indeed)",
		},
		{
			name: "url",
			label: "Website URL",
			type: "text",
			required: true,
			placeholder: "https://example.com",
		},
	];

	// Transform form data before submission
	const transformFormData = (formData) => {
		return {
			...formData,
			name: formData.name?.trim(),
			url: formData.url?.trim() || null,
		};
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			title="Aggregator"
			fields={formFields}
			endpoint="aggregators"
			onSuccess={onSuccess}
			initialData={initialData}
			isEdit={isEdit}
			transformFormData={transformFormData}
			size={size}
		/>
	);
};

export default AggregatorFormModal;