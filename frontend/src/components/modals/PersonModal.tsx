import React from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields, useFormOptions } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { personsApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import AlertModal from "./AlertModal";
import useGenericAlert from "../../hooks/useGenericAlert";
import { DataModalProps } from "./AggregatorModal";
import { PersonData } from "../../services/Schemas";
import { ValidationErrors } from "./GenericModal/GenericModal";

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
	const { companies, openCompanyModal, renderCompanyModal } = useFormOptions(["companies"]);
	const { alertState, hideAlert } = useGenericAlert();
	const { token } = useAuth();

	const formFieldsArray = [
		[formFields.firstName(), formFields.lastName()],
		[formFields.company(companies, openCompanyModal), formFields.role()],
		[formFields.email(), formFields.phone()],
		[formFields.linkedinUrl()],
	];

	const viewFieldsArray = [
		[viewFields.personName({ isTitle: true })],
		[viewFields.companyBadge(), viewFields.role()],
		[viewFields.email(), viewFields.phone()],
		viewFields.linkedinUrl(),
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
			return data?.id !== existing.id;
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
				submode={submode}
				itemName="Person"
				size={size}
				id={id}
				data={data || {}}
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
