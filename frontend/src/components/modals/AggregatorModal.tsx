import React, { forwardRef } from "react";
import DataModal, { DataModalHandle, JamDataModalProps, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { ModalViewField, modalViewFields } from "../rendering/view/ModalFields";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { AggregatorData, AggregatorDataTransform } from "../../services/schemas/DataTables";

export const AggregatorModal = forwardRef<DataModalHandle, JamDataModalProps>(
	({ size = "lg" }: JamDataModalProps, ref) => {
		const dataContext: DataContextValue = useDataContext();

		const fields = {
			form: [
				formFields.name({ required: true, placeholder: "LinkedIn" }),
				formFields.url({ required: true, placeholder: "https://linkedin.com" }),
			],
			view: [modalViewFields.name({ isTitle: true }), modalViewFields.url()],
		};

		const additionalFields: ModalViewField[] = [
			modalViewFields.accordionJobTableAggregator({ helpText: "List of jobs found with this job aggregator." }),
			modalViewFields.accordionJobApplicationTable({
				helpText: "List of job applications made using this job aggregator.",
			}),
		];

		const transformFormData = (data: AggregatorData): AggregatorDataTransform => {
			return {
				name: data?.name?.trim(),
				url: data?.url?.trim(),
			};
		};

		const customValidation = async (formData: AggregatorData): Promise<ValidationErrors> => {
			const errors: ValidationErrors = {};
			const nameDuplicates: AggregatorData[] = dataContext.aggregators.filter(
				(aggregator: AggregatorData): boolean =>
					aggregator.name.toLowerCase() === formData.name.trim().toLowerCase() &&
					aggregator.id !== formData?.id,
			);
			const urlDuplicates: AggregatorData[] = dataContext.aggregators.filter(
				(aggregator: AggregatorData): boolean =>
					aggregator.url.toLowerCase() === formData.url.trim().toLowerCase() &&
					aggregator.id !== formData?.id,
			);

			if (nameDuplicates.length > 0) {
				errors.name = `An aggregator with this name already exists`;
			}
			if (urlDuplicates.length > 0) {
				errors.url = `An aggregator with this URL already exists`;
			}
			return errors;
		};

		return (
			<DataModal
				ref={ref}
				additionalFields={additionalFields}
				size={size}
				fields={fields}
				entityType="aggregator"
				transformFormData={transformFormData}
				validation={customValidation}
			/>
		);
	},
);
