import React from "react";
import DataModal, { DataModalProps, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { aggregatorsApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { AggregatorData, AggregatorDataTransform } from "../../services/Schemas";

export const AggregatorModal: React.FC<DataModalProps> = ({
	show,
	onHide,
	data,
	id,
	submode = "view",
	size = "lg",
}) => {
	const { token } = useAuth();

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

		if (!token) {
			return errors;
		}

		const queryParams = { name: formData.name.trim() };
		const matches = await aggregatorsApi.getAll(token, queryParams);
		const duplicates = matches.filter((existing: { id: number }) => {
			return formData?.id !== existing.id;
		});

		if (duplicates.length > 0) {
			errors.name = `An aggregator with this name already exists`;
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
			id={id}
			fields={fields}
			endpoint="aggregators"
			transformFormData={transformFormData}
			validation={customValidation}
		/>
	);
};
