import React from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { companiesApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { DataModalProps } from "./AggregatorModal";

interface FormData {
	name: string;
	url?: string | null;
	description?: string | null;
}

interface ValidationErrors {
	[key: string]: string;
}

export const CompanyModal: React.FC<DataModalProps> = ({
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
		form: [
			formFields.name({ required: true }),
			[formFields.url({ label: "Website URL" })],
			[formFields.description()],
		],
		view: [viewFields.name({ isTitle: true }), viewFields.url(), [viewFields.description()]],
	};

	const additionalFields = [
		viewFields.jobTable({ excludedColumns: "company" }),
		viewFields.personTable({ excludedColumns: "company" }),
	];

	const transformFormData = (data: FormData): FormData => {
		return {
			name: data.name?.trim(),
			url: data.url?.trim() || null,
			description: data.description?.trim() || null,
		};
	};

	const customValidation = async (formData: FormData): Promise<ValidationErrors> => {
		const errors: ValidationErrors = {};
		if (!formData.name) {
			return errors;
		}
		if (!token) {
			return errors;
		}
		const queryParams = { name: formData.name.trim() };
		const matches = await companiesApi.getAll(token, queryParams);
		const duplicates = matches.filter((existing: any) => {
			return data?.id !== existing.id;
		});

		if (duplicates.length > 0 && formData.name) {
			errors.name = `A company with this name already exists`;
		}

		return errors;
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			submode={submode}
			itemName="Company"
			size={size}
			data={data || {}}
			id={id}
			fields={fields}
			additionalFields={additionalFields}
			endpoint="companies"
			onSuccess={onSuccess}
			onDelete={onDelete}
			transformFormData={transformFormData}
			validation={customValidation}
		/>
	);
};
