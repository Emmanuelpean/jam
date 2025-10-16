import React from "react";
import DataModal, { DataModalProps, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { CompanyData, CompanyDataTransform } from "../../services/Schemas";
import { tableColumns } from "../rendering/view/TableColumns";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";

export const CompanyModal: React.FC<DataModalProps> = ({ show, onHide, data, submode = "view", size = "lg" }) => {
	const dataContext: DataContextValue = useDataContext();

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
		view: [modalViewFields.name({ isTitle: true }), modalViewFields.url(), [modalViewFields.description()]],
	};

	const additionalFields = [
		modalViewFields.accordionJobTableCompany({
			columns: [
				tableColumns.title!(),
				tableColumns.location!(),
				tableColumns.applicationStatus!(),
				tableColumns.createdAt!(),
			],
			helpText: "List of jobs from this company.",
		}),
		modalViewFields.accordionPersonTable({ helpText: "List of persons working at this company." }),
	];

	const transformFormData = (data: CompanyData): CompanyDataTransform => {
		return {
			name: data.name?.trim(),
			url: data.url?.trim() || null,
			description: data.description?.trim() || null,
		};
	};

	const customValidation = async (formData: CompanyData): Promise<ValidationErrors> => {
		const errors: ValidationErrors = {};
		const nameDuplicates: CompanyData[] = dataContext.companies.filter(
			(company: CompanyData): boolean =>
				company.name.toLowerCase() === formData.name.trim().toLowerCase() && company.id !== formData?.id,
		);

		if (nameDuplicates.length > 0) {
			errors.name = `A company with this name already exists`;
		}

		return errors;
	};

	return (
		<DataModal
			show={show}
			onHide={onHide}
			mode={submode}
			itemName="Company"
			size={size}
			data={data}
			fields={fields}
			additionalFields={additionalFields}
			endpoint="companies"
			transformFormData={transformFormData}
			validation={customValidation}
		/>
	);
};
