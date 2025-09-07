import React from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { aggregatorsApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { ValidationErrors } from "./GenericModal/GenericModal";
import { AggregatorData } from "../../services/Schemas";

export interface DataModalProps {
	show: boolean;
	onHide: () => void;
	submode?: "view" | "edit" | "add";
	data?: any;
	id?: number | null;
	onSuccess?: (data: any) => void;
	onDelete?: ((item: any) => Promise<void>) | null;
	size?: "sm" | "lg" | "xl";
}

export const AggregatorModal: React.FC<DataModalProps> = ({
	show,
	onHide,
	data,
	id,
	onSuccess,
	onDelete,
	submode = "view",
	size = "lg",
}) => {
	const { token } = useAuth();

	const fields = {
		form: [formFields.name({ required: true }), formFields.url({ required: true })],
		view: [viewFields.name({ isTitle: true }), viewFields.url()],
	};

	const additionalFields = [viewFields.jobTable()];

	const transformFormData = (data: AggregatorData): AggregatorData => {
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
			return data?.id !== existing.id;
		});

		if (duplicates.length > 0) {
			errors.name = `An aggregator with this name already exists`;
		}
		return errors;
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			submode={submode}
			additionalFields={additionalFields}
			itemName="Aggregator"
			size={size}
			data={data || {}}
			id={id}
			fields={fields}
			endpoint="aggregators"
			onSuccess={onSuccess}
			onDelete={onDelete}
			transformFormData={transformFormData}
			validation={customValidation}
		/>
	);
};
