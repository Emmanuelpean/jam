import React from "react";
import GenericModal from "../GenericModal";
import { formFields } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";
import { keywordsApi } from "../../../services/api";
import {useAuth} from "../../../contexts/AuthContext";

export const KeywordModal = ({
	show,
	onHide,
	keyword,
	onSuccess,
	onDelete,
	endpoint = "keywords",
	submode = "view",
	size = "md",
}) => {
	const { token } = useAuth();

	const formFieldsArray = [formFields.name({ required: true })];
	const viewFieldsArray = [viewFields.name()];
	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	// Transform form data before submission
	const transformFormData = (data) => {
		return {
			...data,
			name: data.name?.trim(),
		};
	};

	// Custom validation to ensure at least one field is filled
	const customValidation = async (formData) => {
		const errors = {};
		const queryParams = { name: formData.name.trim() };
		const matches = await keywordsApi.getAll(token, queryParams);
		const duplicates = matches.filter((existing) => {
			return keyword?.id !== existing.id;
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
			title="Keyword"
			size={size}
			data={keyword || {}}
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
	// Determine the submode based on whether we have keyword data with an ID
	const submode = props.isEdit || props.keyword?.id ? "edit" : "add";
	return <KeywordModal {...props} keyword={props.tag} submode={submode} />;
};

// Wrapper for view modal
export const KeywordViewModal = (props) => <KeywordModal {...props} keyword={props.tag} submode="view" />;

// Add default export
export default KeywordFormModal;
