import React from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { keywordsApi } from "../../services/Api.ts";
import { useAuth } from "../../contexts/AuthContext.tsx";

export const KeywordModal = ({
	show,
	onHide,
	data,
	id,
	onSuccess,
	onDelete,
	endpoint = "keywords",
	submode = "view",
	size = "md",
}) => {
	const { token } = useAuth();

	const fields = {
		form: [formFields.name({ required: true })],
		view: [viewFields.name({ isTitle: true }), viewFields.jobs()],
	};

	const transformFormData = (data) => {
		return {
			name: data?.name?.trim(),
		};
	};

	const customValidation = async (formData) => {
		const errors = {};
		const queryParams = { name: formData.name.trim() };
		const matches = await keywordsApi.getAll(token, queryParams);
		const duplicates = matches.filter((existing) => {
			return data?.id !== existing.id;
		});

		if (duplicates.length > 0) {
			errors.name = `A tag with this name already exists`;
		}
		return errors;
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="formview"
			submode={submode}
			itemName="Tag"
			size={size}
			data={data || {}}
			id={id}
			fields={fields}
			endpoint={endpoint}
			onSuccess={onSuccess}
			onDelete={onDelete}
			transformFormData={transformFormData}
			validation={customValidation}
		/>
	);
};
