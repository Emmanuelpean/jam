import React from "react";
import GenericModal, { DataModalProps } from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { keywordsApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { ValidationErrors } from "./GenericModal/GenericModal";
import { KeywordData } from "../../services/Schemas";

export const KeywordModal: React.FC<DataModalProps> = ({
	show,
	onHide,
	data,
	id,
	onSuccess,
	onDelete,
	submode,
	size = "lg",
}) => {
	const { token } = useAuth();

	const fields = {
		form: [formFields.name({ required: true, placeholder: "Software development" })],
		view: [viewFields.name({ isTitle: true })],
	};

	const additionalFields = [
		viewFields.accordionJobTable({
			helpText: "List of jobs associated with this tag.",
		}),
	];

	const transformFormData = (data: any): KeywordData => {
		return {
			name: data?.name?.trim(),
		};
	};

	const customValidation = async (formData: KeywordData): Promise<ValidationErrors> => {
		const errors: ValidationErrors = {};
		if (!token) {
			return errors;
		}
		const queryParams = { name: formData.name.trim() };
		const matches = await keywordsApi.getAll(token, queryParams);
		const duplicates = matches.filter((existing: any) => {
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
			submode={submode}
			itemName="Tag"
			size={size}
			data={data || {}}
			id={id}
			fields={fields}
			additionalFields={additionalFields}
			endpoint="keywords"
			onSuccess={onSuccess}
			onDelete={onDelete}
			transformFormData={transformFormData}
			validation={customValidation}
		/>
	);
};
