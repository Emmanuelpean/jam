import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, Fields, JamDataModalProps, ValidationErrors } from "./DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { ModalViewField, modalViewFields } from "../rendering/view/ModalFields";
import { useFormOptions } from "../rendering/form/FormOptions";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { CompanyModal } from "./CompanyModal";
import { PersonData, PersonTransform } from "../../services/schemas/DataTables";

export const PersonModal = forwardRef<DataModalHandle, JamDataModalProps>(
	({ size = "lg" }: JamDataModalProps, ref): JSX.Element => {
		const companyModalRef = React.useRef<DataModalHandle>(null);
		const { companies } = useFormOptions();
		const dataContext: DataContextValue = useDataContext();

		const formFieldsArray: Fields = [
			[formFields.firstName({ placeholder: "Jane" }), formFields.lastName({ placeholder: "Doe" })],
			[formFields.company(companies, companyModalRef), formFields.role({ placeholder: "Team Leader" })],
			[formFields.email({ placeholder: "jane.doe@company.com" }), formFields.phone()],
			formFields.linkedinUrl({ placeholder: "https://linkedin.com/in/janedoe" }),
			formFields.isRecruiter(),
		];

		const viewFieldsArray: Fields = [
			[modalViewFields.personName({ isTitle: true })],
			[modalViewFields.companyBadge(), modalViewFields.role()],
			[modalViewFields.email(), modalViewFields.phone()],
			[modalViewFields.linkedinUrl(), modalViewFields.isRecruiter()],
		];

		const fields = {
			form: formFieldsArray,
			view: viewFieldsArray,
		};

		const additionalFields: ModalViewField[] = [
			modalViewFields.accordionInterviewTablePerson({
				helpText: "List of interviews attended by this person.",
			}),
			modalViewFields.accordionJobTablePerson({
				helpText: "List of jobs associated with this person.",
			}),
		];

		const customValidation = async (formData: PersonData): Promise<ValidationErrors> => {
			const errors: ValidationErrors = {};

			const duplicates: PersonData[] = dataContext.persons.filter(
				(person: PersonData): boolean =>
					person.first_name.trim().toLowerCase() === formData.first_name.trim().toLowerCase() &&
					person.last_name.trim().toLowerCase() === formData.last_name.trim().toLowerCase() &&
					person.company_id === formData.company_id &&
					person.id !== formData?.id
			);

			if (duplicates.length > 0) {
				errors.first_name =
					errors.last_name =
					errors.company_id =
						`A person with this name and company already exists`;
			}
			return errors;
		};

		const transformFormData = (data: PersonData): PersonTransform => {
			return {
				first_name: data.first_name?.trim(),
				last_name: data.last_name?.trim(),
				email: data.email?.trim() || null,
				phone: data.phone?.trim() || null,
				role: data.role?.trim() || null,
				linkedin_url: data.linkedin_url?.trim() || null,
				company_id: data.company_id || null,
				is_recruiter: data.is_recruiter,
			};
		};

		return (
			<>
				<DataModal
					ref={ref}
					size={size}
					fields={fields}
					entityType="person"
					validation={customValidation}
					transformFormData={transformFormData}
					additionalFields={additionalFields}
				/>
				<CompanyModal ref={companyModalRef} />
			</>
		);
	}
);
