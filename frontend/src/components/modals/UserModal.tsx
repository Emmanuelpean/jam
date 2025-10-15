import React from "react";
import DataModal, { DataModalProps, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import "../../pages/Auth/Auth.css";
import { UserData, UserDataTransform } from "../../services/Schemas";
import { THEMES } from "../../utils/Theme";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";

export const UserModal: React.FC<DataModalProps> = ({ show, onHide, data, submode = "view", size = "lg" }) => {
	const dataContext: DataContextValue = useDataContext();

	if (submode === "add") {
		data = { theme: THEMES[0]?.key };
	}

	const formFieldsArray = [
		[
			...(submode === "add"
				? [formFields.email({ required: true }), formFields.password({ required: true })]
				: [formFields.email({ required: false })]),
		],
		formFields.appTheme(),
		[formFields.isAdmin(), formFields.toastActive(), formFields.isActive()],
	];
	const viewFieldsArray = [
		[modalViewFields.email(), modalViewFields.appTheme()],
		[modalViewFields.isAdmin(), modalViewFields.toastActive(), modalViewFields.isActive()],
	];

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const customValidation = async (formData: UserData): Promise<ValidationErrors> => {
		const errors: ValidationErrors = {};
		const duplicates = dataContext.users.filter(
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
			show={show}
			onHide={onHide}
			mode={submode}
			itemName="User"
			size={size}
			data={data}
			fields={fields}
			endpoint="users"
			validation={customValidation}
			transformFormData={transformFormData}
		/>
	);
};
