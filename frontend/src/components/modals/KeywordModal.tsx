import React from "react";
import DataModal, { DataModalProps, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { KeywordData, KeywordDataTransform } from "../../services/Schemas";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";

export const KeywordModal: React.FC<DataModalProps> = ({ show, onHide, data, submode, size = "lg" }) => {
	const dataContext: DataContextValue = useDataContext();

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
		const nameDuplicates: KeywordData[] = dataContext.keywords.filter(
			(keyword: KeywordData): boolean =>
				keyword.name.toLowerCase() === formData.name.trim().toLowerCase() && keyword.id !== formData?.id,
		);

		if (nameDuplicates.length > 0) {
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
