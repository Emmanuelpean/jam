import React from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { aggregatorsApi } from "../../services/Api.ts";
import { useAuth } from "../../contexts/AuthContext.tsx";

export const AggregatorModal = ({
	show,
	onHide,
	data,
	onSuccess,
	onDelete,
	endpoint = "aggregators",
	submode = "view",
	size = "lg",
}) => {
	const { token } = useAuth();

	const fields = {
		form: [formFields.name({ required: true }), formFields.url({ required: true })],
		view: [viewFields.name({ isTitle: true }), viewFields.url()],
	};

	const transformFormData = (data) => {
		return {
			name: data?.name?.trim(),
			url: data?.url?.trim(),
		};
	};

	const customValidation = async (formData) => {
		const errors = {};
		const queryParams = { name: formData.name.trim() };
		const matches = await aggregatorsApi.getAll(token, queryParams);
		const duplicates = matches.filter((existing) => {
			return data?.id !== existing.id;
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
			itemName="Aggregator"
			size={size}
			data={data || {}}
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
	const submode = props.isEdit || props.aggregator?.id ? "edit" : "add";
	return <AggregatorModal {...props} submode={submode} />;
};

export const AggregatorViewModal = (props) => <AggregatorModal {...props} submode="view" />;
