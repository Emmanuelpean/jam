import React from "react";
import GenericModal from "../GenericModal";
import { formFields } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";

export const AggregatorModal = ({
									show,
									onHide,
									aggregator,
									onSuccess,
									onDelete,
									endpoint = "aggregators",
									submode = "view",
									size = "lg",
								}) => {
	// Don't render if we're in view mode but have no aggregator data
	if (submode === "view" && !aggregator?.id) {
		return null;
	}

	// Form fields for editing
	const formFieldsArray = [
		[formFields.name({ required: true })],
		[formFields.url({ required: true })],
	];

	// View fields for display
	const viewFieldsArray = [
		[viewFields.name(), viewFields.url()],
	];

	// Combine them in a way GenericModal can use based on mode
	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	// Transform form data before submission
	const transformFormData = (data) => {
		return {
			...data,
			name: data.name?.trim(),
			url: data.url?.trim() || null,
		};
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="formview"
			submode={submode}
			title="Aggregator"
			size={size}
			data={aggregator || {}}
			fields={fields}
			endpoint={endpoint}
			onSuccess={onSuccess}
			onDelete={onDelete}
			transformFormData={transformFormData}
		/>
	);
};

export const AggregatorFormModal = (props) => {
	// Determine the submode based on whether we have aggregator data with an ID
	const submode = props.isEdit || props.aggregator?.id ? "edit" : "add";
	return <AggregatorModal {...props} submode={submode} />;
};

// Wrapper for view modal
export const AggregatorViewModal = (props) => <AggregatorModal {...props} submode="view" />;

// Add default export
export default AggregatorFormModal;