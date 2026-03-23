import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, Fields, JamDataModalProps, ValidationErrors } from "./DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { ScrapingFilterData, ScrapingFilterTransform } from "../../services/schemas/Services";

interface ScrapingFilterModalProps extends JamDataModalProps {
	variant?: "scraping" | "favourite";
}

export const ScrapingFilterModal = forwardRef<DataModalHandle, ScrapingFilterModalProps>(
	({ size = "lg", variant = "scraping" }: ScrapingFilterModalProps, ref): JSX.Element => {
		const dataContext: DataContextValue = useDataContext();
		const isScraping = variant === "scraping";

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

			const filters = isScraping ? dataContext.scrapingFilters : dataContext.scrapingFavouriteFilters;
			const duplicates: ScrapingFilterData[] = filters.filter(
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

		const canEdit = isScraping
			? (formData: ScrapingFilterData): string => {
					if (formData?.filtered_jobs?.length > 0) {
						return "Filters that have been applied to scraped jobs cannot be edited.";
					}
					return "";
			  }
			: undefined;

		const canDelete = isScraping
			? (formData: ScrapingFilterData): string => {
					if (formData?.filtered_jobs?.length > 0) {
						return "Filters that have been applied to scraped jobs cannot be deleted.";
					}
					return "";
			  }
			: undefined;

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
				entityType={isScraping ? "scrapingFilter" : "scrapingFavouriteFilter"}
				validation={customValidation}
				transformFormData={transformFormData}
				{...(isScraping && {
					additionalFields: [modalViewFields.accordionScrapedJobTable()],
					canEdit,
					canDelete,
				})}
				showDeactivate={true}
			/>
		);
	}
);
