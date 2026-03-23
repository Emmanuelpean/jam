import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, Fields, JamDataModalProps, ValidationErrors } from "./DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { ScrapingFilterData, ScrapingFilterTransform } from "../../services/schemas/Services";

export const FavouriteFilterModal = forwardRef<DataModalHandle, JamDataModalProps>(
	({ size = "lg" }: JamDataModalProps, ref): JSX.Element => {
		const dataContext: DataContextValue = useDataContext();

		const formFieldsArray: Fields = [
			formFields.scrapingFilterType(),
			formFields.scrapingFilterOperator(),
			formFields.value({ type: "input", placeholder: "Enter a value" }),
			formFields.caseSensitive(),
		];

		const viewFieldsArray: Fields = [
			modalViewFields.scrapingFilterName({ isTitle: true }),
			modalViewFields.caseSensitive(),
		];

		const fields = {
			form: formFieldsArray,
			view: viewFieldsArray,
		};

		const customValidation = async (formData: ScrapingFilterData): Promise<ValidationErrors> => {
			const errors: ValidationErrors = {};

			const duplicates: ScrapingFilterData[] = dataContext.scrapingFavouriteFilters.filter(
				(filter: ScrapingFilterData): boolean =>
					filter.type === formData.type &&
					filter.operator === formData.operator &&
					filter.value.trim().toLowerCase() === formData.value.trim().toLowerCase() &&
					filter.case_sensitive === formData.case_sensitive &&
					filter.id !== formData?.id
			);

			if (duplicates.length > 0) {
				errors.type = errors.operator = errors.value = `A filter with these values already exists`;
			}
			return errors;
		};

		const transformFormData = (formData: ScrapingFilterData): ScrapingFilterTransform => {
			return {
				type: formData.type,
				operator: formData.operator,
				value: formData.value.trim(),
				case_sensitive: formData.case_sensitive,
			};
		};

		return (
			<DataModal
				ref={ref}
				size={size}
				fields={fields}
				entityType="scrapingFavouriteFilter"
				validation={customValidation}
				transformFormData={transformFormData}
				showDeactivate={true}
			/>
		);
	}
);