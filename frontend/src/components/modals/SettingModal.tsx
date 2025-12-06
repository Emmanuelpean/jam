import React from "react";
import DataModal, { DataModalProps, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { SettingData, SettingDataTransform } from "../../services/Schemas";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";

export const SettingModal: React.FC<DataModalProps> = ({ size = "lg" }) => {
	const dataContext: DataContextValue = useDataContext();

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
		const duplicates = dataContext.settings.filter(
			(setting: SettingData) =>
				setting.name.trim().toLowerCase() === formData.name.trim().toLowerCase() && setting.id !== formData?.id,
		);
		if (duplicates.length > 0) {
			errors.name = `A setting with this name already exists`;
		}
		return errors;
	};

	return (
		<DataModal
			itemName="Setting"
			size={size}
			fields={fields}
			endpoint="settings"
			transformFormData={transformFormData}
			validation={customValidation}
		/>
	);
};
