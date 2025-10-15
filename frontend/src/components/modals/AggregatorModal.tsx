import React from "react";
import DataModal, { DataModalProps, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { AggregatorData, AggregatorDataTransform } from "../../services/Schemas";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";

export const AggregatorModal: React.FC<DataModalProps> = ({ show, onHide, data, submode = "view", size = "lg" }) => {
	const dataContext: DataContextValue = useDataContext();

	const fields = {
		form: [
			formFields.name({ required: true, placeholder: "LinkedIn" }),
			formFields.url({ required: true, placeholder: "https://linkedin.com" }),
		],
		view: [modalViewFields.name({ isTitle: true }), modalViewFields.url()],
	};

	const additionalFields = [
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
				aggregator.name.toLowerCase() === formData.name.trim().toLowerCase() && aggregator.id !== formData?.id,
		);
		const urlDuplicates: AggregatorData[] = dataContext.aggregators.filter(
			(aggregator: AggregatorData): boolean =>
				aggregator.url.toLowerCase() === formData.url.trim().toLowerCase() && aggregator.id !== formData?.id,
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
			show={show}
			onHide={onHide}
			mode={submode}
			additionalFields={additionalFields}
			itemName="Aggregator"
			size={size}
			data={data}
			fields={fields}
			endpoint="aggregators"
			transformFormData={transformFormData}
			validation={customValidation}
		/>
	);
};
