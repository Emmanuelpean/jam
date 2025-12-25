import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, JamDataModalProps, Fields, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { ScrapedJobFilterData, ScrapedJobFilterTransform } from "../../services/Schemas";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";

export const ScrapedJobFilterModal = forwardRef<DataModalHandle, JamDataModalProps>(
	({ size = "lg" }: JamDataModalProps, ref): JSX.Element => {
		const dataContext: DataContextValue = useDataContext();

		const formFieldsArray: Fields = [
			formFields.scrapedJobFilterType(),
			formFields.scrapedJobFilterOperator(),
			formFields.value({ type: "input", placeholder: "Enter a value" }),

			[formFields.isEnabled(), formFields.caseSensitive()],
		];

		const viewFieldsArray: Fields = [
			modalViewFields.scrapedJobFilterName({ isTitle: true }),
			[modalViewFields.isEnabled(), modalViewFields.caseSensitive()],
		];

		const fields = {
			form: formFieldsArray,
			view: viewFieldsArray,
		};

		const customValidation = async (formData: ScrapedJobFilterData): Promise<ValidationErrors> => {
			const errors: ValidationErrors = {};

			const duplicates: ScrapedJobFilterData[] = dataContext.scrapedJobFilters.filter(
				(filter: ScrapedJobFilterData): boolean =>
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

		const canEdit = (formData: ScrapedJobFilterData) => {
			console.log(formData);
			if (formData?.filtered_jobs?.length > 0) {
				return "Filters that have been applied to scraped jobs cannot be edited.";
			} else {
				return "";
			}
		};

		const canDeactivate = (formData: ScrapedJobFilterData) => {
			if (formData?.filtered_jobs?.length > 0) {
				return "it having been used to filter scraped jobs";
			} else {
				return "";
			}
		};

		const transformFormData = (formData: ScrapedJobFilterData): ScrapedJobFilterTransform => {
			return {
				type: formData.type,
				operator: formData.operator,
				value: formData.value.trim(),
				is_active: formData.is_enabled,
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
					additionalFields={[modalViewFields.accordionScrapedJobTable()]}
					canEdit={canEdit}
					canDeactivate={canDeactivate}
				/>
			</>
		);
	},
);
