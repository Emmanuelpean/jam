import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, JamDataModalProps, Fields, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { ScrapingFilterData, ScrapingFilterTransform } from "../../services/Schemas";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";

export const ScrapingFilterModal = forwardRef<DataModalHandle, JamDataModalProps>(
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

			const duplicates: ScrapingFilterData[] = dataContext.scrapingFilters.filter(
				(filter: ScrapingFilterData): boolean =>
					filter.type === formData.type &&
					filter.operator === formData.operator &&
					filter.value.trim().toLowerCase() === formData.value.trim().toLowerCase() &&
					filter.case_sensitive === formData.case_sensitive &&
					filter.id !== formData?.id,
			);

			if (duplicates.length > 0) {
				errors.type = errors.operator = errors.value = `A filter with these values already exist`;
			}
			return errors;
		};

		const canEdit = (formData: ScrapingFilterData): string => {
			if (formData?.filtered_jobs?.length > 0) {
				return "Filters that have been applied to scraped jobs cannot be edited.";
			} else {
				return "";
			}
		};

		const canDelete = (formData: ScrapingFilterData): string => {
			if (formData?.filtered_jobs?.length > 0) {
				return "Filters that have been applied to scraped jobs cannot be deleted.";
			} else {
				return "";
			}
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
			<>
				<DataModal
					ref={ref}
					itemName="Scraping Filter"
					size={size}
					fields={fields}
					endpoint="scraping-filters"
					validation={customValidation}
					transformFormData={transformFormData}
					additionalFields={[modalViewFields.accordionScrapedJobTable()]}
					canEdit={canEdit}
					canDelete={canDelete}
					showDeactivate={true}
				/>
			</>
		);
	},
);
