import React from "react";
import GenericModal from "./GenericModal";
import { formFields } from "../rendering/FormRenders";
import { viewFields } from "../rendering/ViewRenders";
import { keywordsApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";

export const KeywordModal = ({
	show,
	onHide,
	data,
	onSuccess,
	onDelete,
	endpoint = "keywords",
	submode = "view",
	size = "md",
}) => {
	const { token } = useAuth();

	const fields = {
		form: [formFields.name({ required: true })],
		view: [viewFields.name()],
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
			fields={fields}
			endpoint={endpoint}
			onSuccess={onSuccess}
			onDelete={onDelete}
			transformFormData={transformFormData}
			validation={customValidation}
		/>
	);
};

export const KeywordFormModal = (props) => {
	const submode = props.isEdit || props.keyword?.id ? "edit" : "add";
	return <KeywordModal {...props} submode={submode} />;
};

export const KeywordViewModal = (props) => <KeywordModal {...props} submode="view" />;
