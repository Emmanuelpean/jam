import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, JamDataModalProps, ValidationErrors } from "./DataModal";
import { useFormFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { SettingData, SettingDataTransform } from "../../services/schemas/Core";

export const SettingModal = forwardRef<DataModalHandle<SettingData>, JamDataModalProps>(
	({ size = "xl" }: JamDataModalProps, ref): JSX.Element => {
		const dataContext: DataContextValue = useDataContext();
		const ff = useFormFields();

		const fields = {
			form: [
				ff.nameField({ required: true, placeholder: "allowlist" }),
				ff.valueField({ required: true, placeholder: "test_user@test.com" }),
				ff.descriptionField({
					placeholder: "Allow only those email addresses to sign up.",
				}),
				ff.isActiveField(),
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

		const customValidation = (formData: SettingData): ValidationErrors => {
			const errors: ValidationErrors = {};
			const duplicates: SettingData[] = dataContext.settings.filter(
				(setting: SettingData): boolean =>
					setting.name.trim().toLowerCase() === formData.name.trim().toLowerCase() &&
					setting.id !== formData?.id
			);
			if (duplicates.length > 0) {
				errors.name = `A setting with this name already exists`;
			}
			return errors;
		};

		return (
			<DataModal<SettingData>
				ref={ref}
				size={size}
				fields={fields}
				entityType="setting"
				transformFormData={transformFormData}
				validation={customValidation}
			/>
		);
	}
);
