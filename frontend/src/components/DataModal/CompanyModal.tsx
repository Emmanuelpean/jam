import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, JamDataModalProps, ValidationErrors } from "./DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { ModalViewField, modalViewFields } from "../rendering/view/ModalFields";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { CompanyData, CompanyDataTransform } from "../../services/schemas/DataTables";

export const CompanyModal = forwardRef<DataModalHandle<CompanyData>, JamDataModalProps>(
	({ size = "lg" }: JamDataModalProps, ref): JSX.Element => {
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

		const jobTableColumns: TableColumn[] = [
			tableColumns.titleColumn(),
			tableColumns.locationBadgeColumn(),
			tableColumns.applicationStatusColumn(),
			tableColumns.createdAtColumn(),
		];
		const additionalFields: ModalViewField[] = [
			modalViewFields.accordionJobTableCompany({
				columns: jobTableColumns,
				helpText: "Jobs from this company.",
			}),
			modalViewFields.accordionPersonTable({
				helpText: "Persons working at this company.",
			}),
			modalViewFields.accordionRecruitedJobTableCompany({
				columns: jobTableColumns,
				helpText: "Jobs shared with you by this recruitment company.",
			}),
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
					company.name.toLowerCase() === formData.name.trim().toLowerCase() && company.id !== formData?.id
			);

			if (nameDuplicates.length > 0) {
				errors.name = `A company with this name already exists`;
			}

			return errors;
		};

		return (
			<DataModal<CompanyData>
				ref={ref}
				size={size}
				fields={fields}
				additionalFields={additionalFields}
				entityType="company"
				transformFormData={transformFormData}
				validation={customValidation}
			/>
		);
	}
);
