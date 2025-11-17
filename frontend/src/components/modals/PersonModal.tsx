import React from "react";
import DataModal, { DataModalProps, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { PersonData, PersonTransform } from "../../services/Schemas";
import { useFormOptions } from "../rendering/form/FormOptions";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";

export const PersonModal: React.FC<DataModalProps> = ({ show, onHide, data, submode = "view", size = "lg" }) => {
	const { companies, openCompanyModal, renderCompanyModal, getCompanyPreviewConfig } = useFormOptions(
		show ? ["companies"] : [],
	);
	console.log(getCompanyPreviewConfig);
	const dataContext: DataContextValue = useDataContext();

	const formFieldsArray = [
		[formFields.firstName({ placeholder: "Jane" }), formFields.lastName({ placeholder: "Doe" })],
		[
			formFields.company(companies, openCompanyModal, getCompanyPreviewConfig()),
			formFields.role({ placeholder: "Team Leader" }),
		],
		[formFields.email({ placeholder: "jane.doe@company.com" }), formFields.phone()],
		[formFields.linkedinUrl({ placeholder: "https://linkedin.com/in/janedoe" })],
	];

	const viewFieldsArray = [
		[modalViewFields.personName({ isTitle: true })],
		[modalViewFields.companyBadge(), modalViewFields.role()],
		[modalViewFields.email(), modalViewFields.phone()],
		modalViewFields.linkedinUrl(),
	];

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const additionalFields = [
		modalViewFields.accordionInterviewTablePerson({ helpText: "List of interviews attended by this person." }),
		modalViewFields.accordionJobTablePerson({ helpText: "List of jobs associated with this person." }),
	];

	const customValidation = async (formData: PersonData): Promise<ValidationErrors> => {
		const errors: ValidationErrors = {};

		const duplicates: PersonData[] = dataContext.persons.filter(
			(person: PersonData): boolean =>
				person.first_name.trim().toLowerCase() === formData.first_name.trim().toLowerCase() &&
				person.last_name.trim().toLowerCase() === formData.last_name.trim().toLowerCase() &&
				person.company_id === formData.company_id &&
				person.id !== formData?.id,
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
		};
	};

	return (
		<>
			<DataModal
				show={show}
				onHide={onHide}
				mode={submode}
				itemName="Person"
				size={size}
				data={data}
				fields={fields}
				endpoint="persons"
				validation={customValidation}
				transformFormData={transformFormData}
				additionalFields={additionalFields}
			/>

			{renderCompanyModal()}
		</>
	);
};
