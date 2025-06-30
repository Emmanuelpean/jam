import React from "react";
import GenericModal from "../GenericModal";
import { formFields } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";
import {aggregatorsApi} from "../../../services/api";
import {useAuth} from "../../../contexts/AuthContext";

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
	const { token } = useAuth();

	const formFieldsArray = [[formFields.name({ required: true })], [formFields.url({ required: true })]];
	const viewFieldsArray = [[viewFields.name(), viewFields.url()]];
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

	// Custom validation to ensure at least one field is filled
	const customValidation = async (formData) => {
		const errors = {};
		const queryParams = {name: formData.name.trim()};
		const matches = await aggregatorsApi.getAll(token, queryParams);
		const duplicates = matches.filter((existing) => {
			return aggregator?.id !== existing.id;
		});

		if (duplicates.length > 0) {
			errors.name = `An aggregator with this name already exists`;
		}

		return errors;
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
			validation={customValidation}
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
