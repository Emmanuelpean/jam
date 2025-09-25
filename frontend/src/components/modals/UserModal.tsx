import React from "react";
import GenericModal, { DataModalProps } from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { userApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import "../../pages/Auth/Auth.css";
import { ValidationErrors } from "./GenericModal/GenericModal";
import { UserData } from "../../services/Schemas";
import { THEMES } from "../../utils/Theme";

export const UserModal: React.FC<DataModalProps> = ({
	show,
	onHide,
	data,
	id,
	onSuccess,
	onDelete,
	submode = "view",
	size = "lg",
}) => {
	const { token } = useAuth();

	const formFieldsArray = [
		[
			...(submode === "add"
				? [formFields.email({ required: true }), formFields.password({ required: true })]
				: [formFields.email({ required: false })]),
		],
		formFields.appTheme(),
		formFields.isAdmin(),
	];
	const viewFieldsArray = [[modalViewFields.email(), modalViewFields.appTheme(), modalViewFields.isAdmin()]];

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

	const transformFormData = (data: UserData) => {
		const transformed: any = {
			email: data.email?.trim(),
			theme: data.theme?.trim() || THEMES[0],
			is_admin: data.is_admin || false,
		};

		return transformed;
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode={submode}
			itemName="User"
			size={size}
			data={data}
			id={id}
			fields={fields}
			endpoint="users"
			onSuccess={onSuccess}
			onDelete={onDelete}
			validation={customValidation}
			transformFormData={transformFormData}
		/>
	);
};
