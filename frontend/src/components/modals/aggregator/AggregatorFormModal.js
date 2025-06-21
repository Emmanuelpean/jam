
import React from "react";
import GenericModal from "../GenericModal";
import { formFields } from "../../rendering/FormRenders";

const AggregatorFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false }) => {

	const aggregatorFields = [
		formFields.name({
			required: true,
		}),
		formFields.url({
			required: true,
		}),
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
			mode="form"
			title="Aggregator"
			fields={aggregatorFields}
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