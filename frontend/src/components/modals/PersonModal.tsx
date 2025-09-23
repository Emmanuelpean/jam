import React from "react";
import GenericModal, { DataModalProps } from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { personsApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import AlertModal from "./AlertModal";
import useGenericAlert from "../../hooks/useGenericAlert";
import { PersonData } from "../../services/Schemas";
import { ValidationErrors } from "./GenericModal/GenericModal";
import { useFormOptions } from "../rendering/form/FormOptions";

export const PersonModal: React.FC<DataModalProps> = ({
	show,
	onHide,
	data,
	id = null,
	onSuccess,
	onDelete,
	submode = "view",
	size = "lg",
}) => {
	const { companies, openCompanyModal, renderCompanyModal } = useFormOptions(show ? ["companies"] : []);
	const { alertState, hideAlert } = useGenericAlert();
	const { token } = useAuth();

	const formFieldsArray = [
		[formFields.firstName({ placeholder: "Jane" }), formFields.lastName({ placeholder: "Doe" })],
		[formFields.company(companies, openCompanyModal), formFields.role({ placeholder: "Team Leader" })],
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

	const customValidation = async (formData: PersonData): Promise<ValidationErrors> => {
		const errors: ValidationErrors = {};

		if (!token) {
			return errors;
		}

		const queryParams = {
			first_name: formData.first_name.trim(),
			last_name: formData.last_name.trim(),
			company_id: formData.company_id,
		};
		const matches = await personsApi.getAll(token, queryParams);
		const duplicates = matches.filter((existing: any) => {
			return formData?.id !== existing.id;
		});

		if (duplicates.length > 0) {
			errors.first_name =
				errors.last_name =
				errors.company_id =
					`A person with this name and company already exists`;
		}
		return errors;
	};

	const transformFormData = (data: PersonData) => {
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
			<GenericModal
				show={show}
				onHide={onHide}
				mode={submode}
				itemName="Person"
				size={size}
				id={id}
				data={data}
				fields={fields}
				endpoint="persons"
				onSuccess={onSuccess}
				onDelete={onDelete}
				validation={customValidation}
				transformFormData={transformFormData}
			/>

			{renderCompanyModal()}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};
