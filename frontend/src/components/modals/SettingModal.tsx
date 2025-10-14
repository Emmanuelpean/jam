import React from "react";
import DataModal, { DataModalProps, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { settingsApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { SettingData, SettingDataTransform } from "../../services/Schemas";

export const SettingModal: React.FC<DataModalProps> = ({ show, onHide, data, submode, size = "lg" }) => {
	const { token } = useAuth();

	const fields = {
		form: [
			formFields.name({ required: true, placeholder: "allowlist" }),
			formFields.value({ required: true, placeholder: "test_user@test.com" }),
			formFields.description({ placeholder: "Allow only those email addresses to sign up." }),
			formFields.isActive(),
		],
		view: [
			modalViewFields.name(),
			modalViewFields.value(),
			modalViewFields.description(),
			modalViewFields.isActive(),
		],
	};

	const transformFormData = (data: SettingData): SettingDataTransform => {
		return {
			name: data?.name?.trim(),
			value: data?.value?.trim(),
			description: data?.description?.trim(),
			is_active: data?.is_active,
		};
	};

	const customValidation = async (formData: SettingData): Promise<ValidationErrors> => {
		const errors: ValidationErrors = {};
		if (!token) {
			return errors;
		}
		const queryParams = { name: formData.name.trim() };
		const matches = await settingsApi.getAll(token, queryParams);
		const duplicates = matches.filter((existing: SettingData) => {
			return formData?.id !== existing.id;
		});

		if (duplicates.length > 0) {
			errors.name = `A setting with this name already exists`;
		}
		return errors;
	};

	return (
		<DataModal
			show={show}
			onHide={onHide}
			mode={submode}
			itemName="Setting"
			size={size}
			data={data}
			fields={fields}
			endpoint="settings"
			transformFormData={transformFormData}
			validation={customValidation}
		/>
	);
};
