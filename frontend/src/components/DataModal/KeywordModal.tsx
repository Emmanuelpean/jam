import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, JamDataModalProps, ValidationErrors } from "./DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { ModalViewField, modalViewFields } from "../rendering/view/ModalFields";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { KeywordData, KeywordDataTransform } from "../../services/schemas/DataTables";

export const KeywordModal = forwardRef<DataModalHandle, JamDataModalProps>(
	({ size = "lg" }: JamDataModalProps, ref): JSX.Element => {
		const dataContext: DataContextValue = useDataContext();

		const fields = {
			form: [formFields.name({ required: true, placeholder: "Software development" })],
			view: [modalViewFields.name({ isTitle: true })],
		};

		const additionalFields: ModalViewField[] = [
			modalViewFields.accordionJobTableKeyword({
				helpText: "Jobs associated with this tag.",
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
					keyword.name.toLowerCase() === formData.name.trim().toLowerCase() && keyword.id !== formData?.id
			);
			if (nameDuplicates.length > 0) {
				errors.name = `A tag with this name already exists`;
			}
			return errors;
		};

		return (
			<DataModal
				ref={ref}
				size={size}
				fields={fields}
				additionalFields={additionalFields}
				entityType="keyword"
				transformFormData={transformFormData}
				validation={customValidation}
			/>
		);
	}
);
