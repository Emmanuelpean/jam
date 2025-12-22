import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, JamDataModalProps, Fields, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import "../../pages/Auth/Auth.css";
import { UserData, UserDataTransform } from "../../services/Schemas";
import { THEMES } from "../../utils/Theme";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";

export const UserModal = forwardRef<DataModalHandle, JamDataModalProps>(({ size = "lg" }, ref): JSX.Element => {
	const dataContext: DataContextValue = useDataContext();

	const createFields = (data: any, mode: string): { form: Fields; view: Fields } => {
		const isAddMode: boolean = mode === "add" || !data?.id;

		const formFieldsArray: Fields = [
			[formFields.email({ required: true }), ...(isAddMode ? [formFields.password({ required: true })] : [])],
			formFields.appTheme(),
			[formFields.isAdmin(), formFields.toastActive(), formFields.isActive()],
		];

		const viewFieldsArray: Fields = [
			[modalViewFields.email(), modalViewFields.appTheme()],
			[modalViewFields.isAdmin(), modalViewFields.toastActive(), modalViewFields.isActive()],
		];

		return {
			form: formFieldsArray,
			view: viewFieldsArray,
		};
	};

	const customValidation = async (formData: UserData): Promise<ValidationErrors> => {
		const errors: ValidationErrors = {};
		const duplicates: UserData[] = dataContext.users.filter(
			(user: UserData): boolean =>
				user.email.trim().toLowerCase() === formData.email.trim().toLowerCase() && user.id !== formData?.id,
		);
		if (duplicates.length > 0) {
			errors.email = `A user with this email address already exists`;
		}
		return errors;
	};

	const transformFormData = (formData: UserDataTransform): UserDataTransform => {
		return {
			email: formData.email?.trim(),
			password: formData.password?.trim(),
			theme: formData.theme || THEMES[0]?.key,
			is_admin: formData.is_admin || false,
			toast_active: formData.toast_active || false,
			is_active: formData.is_active || false,
		};
	};

	return (
		<DataModal
			ref={ref}
			itemName="User"
			size={size}
			fields={createFields}
			endpoint="users"
			validation={customValidation}
			transformFormData={transformFormData}
		/>
	);
});
