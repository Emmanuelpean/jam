import React from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { userApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import "../../pages/Auth/Auth.css";
import { DataModalProps } from "./AggregatorModal";
import { ValidationErrors } from "./GenericModal/GenericModal";
import { UserData } from "../../services/Schemas";

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
	const viewFieldsArray = [[viewFields.email(), viewFields.appTheme()], viewFields.isAdmin()];

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
		const duplicates = matches.filter((existing: any) => {
			return data?.id !== existing.id;
		});
		console.log(duplicates);

		if (duplicates.length > 0) {
			errors.email = `A tag with this name already exists`;
		}
		return errors;
	};

	const transformFormData = (data: UserData) => {
		const transformed: any = {
			email: data.email?.trim(),
			theme: data.theme?.trim() || "mixed-berry",
			is_admin: data.is_admin || false,
		};

		if (data.password) {
			transformed.password = data.password;
		}

		return transformed;
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			submode={submode}
			itemName="User"
			size={size}
			data={data || {}}
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
