import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, JamDataModalProps, ValidationErrors } from "./DataModal";
import { useFormFields } from "../rendering/form/FormRenders";
import { ModalViewField, modalViewFields } from "../rendering/view/ModalFields";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { CompanyData, CompanyDataTransform } from "../../services/schemas/DataTables";

export const CompanyModal = forwardRef<DataModalHandle<CompanyData>, JamDataModalProps>(
	({ size = "lg" }: JamDataModalProps, ref): JSX.Element => {
		const dataContext: DataContextValue = useDataContext();
		const ff = useFormFields();

		const fields = {
			form: [
				ff.nameField({ required: true, placeholder: "Google" }),
				[ff.urlField({ label: "Website URL", placeholder: "https://www.google.com" })],
				[
					ff.descriptionField({
						placeholder:
							"Google is a global technology company best known for its search engine, which organises " +
							"and provides access to information across the internet, alongside a wide range of digital " +
							"services and products.",
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

		const customValidation = (formData: CompanyData): ValidationErrors => {
			const errors: ValidationErrors = {};
			const nameDuplicates: CompanyData[] = dataContext.companies.filter(
				(company: CompanyData): boolean =>
					company.name.toLowerCase() === formData.name?.trim().toLowerCase() && company.id !== formData?.id
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
