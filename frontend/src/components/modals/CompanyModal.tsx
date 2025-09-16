import React from "react";
import GenericModal, { DataModalProps } from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { companiesApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { ValidationErrors } from "./GenericModal/GenericModal";
import { CompanyData } from "../../services/Schemas";
import { tableColumns } from "../rendering/view/TableColumnRenders";

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
			formFields.name({ required: true, placeholder: "Google" }),
			[formFields.url({ label: "Website URL", placeholder: "https://www.google.com" })],
			[
				formFields.description({
					placeholder:
						"Google is a global technology company best known for its search engine, which organises and provides access to information across the internet, alongside a wide range of digital services and products.",
				}),
			],
		],
		view: [viewFields.name({ isTitle: true }), viewFields.url(), [viewFields.description()]],
	};

	const additionalFields = [
		viewFields.accordionJobTable({
			columns: [
				tableColumns.title!(),
				tableColumns.location!(),
				tableColumns.applicationStatus!(),
				tableColumns.createdAt!(),
			],
			helpText: "List of jobs from this company.",
		}),
		viewFields.accordionPersonTable({ helpText: "List of persons working at this company." }),
	];

	const transformFormData = (data: CompanyData): CompanyData => {
		return {
			name: data.name?.trim(),
			url: data.url?.trim() || null,
			description: data.description?.trim() || null,
		};
	};

	const customValidation = async (formData: CompanyData): Promise<ValidationErrors> => {
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
