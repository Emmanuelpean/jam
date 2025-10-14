import React from "react";
import DataModal, { DataModalProps } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { keywordsApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { ValidationErrors } from "./DataModal/DataModal";
import { KeywordData, KeywordDataTransform } from "../../services/Schemas";

export const KeywordModal: React.FC<DataModalProps> = ({ show, onHide, data, submode, size = "lg" }) => {
	const { token } = useAuth();

	const fields = {
		form: [formFields.name({ required: true, placeholder: "Software development" })],
		view: [modalViewFields.name({ isTitle: true })],
	};

	const additionalFields = [
		modalViewFields.accordionJobTableKeyword({
			helpText: "List of jobs associated with this tag.",
		}),
	];

	const transformFormData = (data: KeywordData): KeywordDataTransform => {
		return {
			name: data.name.trim(),
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
			return formData?.id !== existing.id;
		});

		if (duplicates.length > 0) {
			errors.name = `A tag with this name already exists`;
		}
		return errors;
	};

	return (
		<DataModal
			show={show}
			onHide={onHide}
			mode={submode}
			itemName="Tag"
			size={size}
			data={data}
			fields={fields}
			additionalFields={additionalFields}
			endpoint="keywords"
			transformFormData={transformFormData}
			validation={customValidation}
		/>
	);
};
