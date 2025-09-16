import React from "react";
import GenericModal, { DataModalProps, ValidationErrors } from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { settingsApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { SettingData } from "../../services/Schemas";

export const SettingModal: React.FC<DataModalProps> = ({
	show,
	onHide,
	data,
	id,
	onSuccess,
	onDelete,
	submode,
	size = "lg",
}) => {
	const { token } = useAuth();

	const fields = {
		form: [
			formFields.name({ required: true, placeholder: "allowlist" }),
			formFields.value({ required: true, placeholder: "test_user@test.com" }),
			formFields.description({ placeholder: "Allow only those email addresses to sign up." }),
		],
		view: [viewFields.name(), viewFields.value(), viewFields.description()],
	};

	const transformFormData = (data: any): SettingData => {
		return {
			name: data?.name?.trim(),
			value: data?.value?.trim(),
			description: data?.description?.trim(),
		};
	};

	const customValidation = async (formData: SettingData): Promise<ValidationErrors> => {
		const errors: ValidationErrors = {};
		if (!token) {
			return errors;
		}
		const queryParams = { name: formData.name.trim() };
		const matches = await settingsApi.getAll(token, queryParams);
		const duplicates = matches.filter((existing: any) => {
			return data?.id !== existing.id;
		});

		if (duplicates.length > 0) {
			errors.name = `A setting with this name already exists`;
		}
		return errors;
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			submode={submode}
			itemName="Tag"
			size={size}
			data={data || {}}
			id={id}
			fields={fields}
			endpoint="settings"
			onSuccess={onSuccess}
			onDelete={onDelete}
			transformFormData={transformFormData}
			validation={customValidation}
		/>
	);
};
