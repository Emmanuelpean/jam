import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, DataModalProps, Fields, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { ScrapedJobFilter, ScrapedJobFilterTransform } from "../../services/Schemas";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";

export const ScrapedJobFilterModal = forwardRef<DataModalHandle, DataModalProps>(
	({ size = "lg" }: DataModalProps, ref): JSX.Element => {
		const dataContext: DataContextValue = useDataContext();

		const formFieldsArray: Fields = [
			formFields.scrapedJobFilterType(),
			formFields.scrapedJobFilterOperator(),
			formFields.value({ type: "input", placeholder: "Enter a value" }),

			[formFields.isActive(), formFields.caseSensitive()],
		];

		const viewFieldsArray: Fields = [
			modalViewFields.scrapedJobFilterName({ isTitle: true }),
			[modalViewFields.isActive(), modalViewFields.caseSensitive()],
		];

		const fields = {
			form: formFieldsArray,
			view: viewFieldsArray,
		};

		const customValidation = async (formData: ScrapedJobFilter): Promise<ValidationErrors> => {
			const errors: ValidationErrors = {};

			const duplicates: ScrapedJobFilter[] = dataContext.scrapedJobFilters.filter(
				(filter: ScrapedJobFilter): boolean =>
					filter.type === formData.type &&
					filter.operator === formData.operator &&
					filter.value.trim().toLowerCase() === formData.value.trim().toLowerCase() &&
					filter.id !== formData?.id,
			);

			if (duplicates.length > 0) {
				errors.type = errors.operator = errors.value = `A filter with these values already exist`;
			}
			return errors;
		};

		const transformFormData = (formData: ScrapedJobFilter): ScrapedJobFilterTransform => {
			return {
				type: formData.type,
				operator: formData.operator,
				value: formData.value.trim(),
				is_active: formData.is_active,
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
					endpoint="scraped_job_filters"
					validation={customValidation}
					transformFormData={transformFormData}
				/>
			</>
		);
	},
);
