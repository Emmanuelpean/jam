import React from "react";
import DataModal, { DataModalProps } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { userApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import "../../pages/Auth/Auth.css";
import { ValidationErrors } from "./DataModal/DataModal";
import { UserData, UserDataTransform } from "../../services/Schemas";
import { THEMES } from "../../utils/Theme";

export const UserModal: React.FC<DataModalProps> = ({ show, onHide, data, submode = "view", size = "lg" }) => {
	const { token } = useAuth();

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
		if (!token) {
			return errors;
		}
		const queryParams = { email: formData.email.trim() };
		const matches = await userApi.getAll(token, queryParams);
		const duplicates = matches.filter((existing: UserData) => {
			return formData?.id !== existing.id;
		});

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
