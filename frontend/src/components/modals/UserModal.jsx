import React from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ViewRenders";
import { userApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import "../../pages/Auth/Login.css";

export const UserModal = ({
	show,
	onHide,
	data,
	onSuccess,
	onDelete,
	endpoint = "users",
	submode = "view",
	size = "lg",
}) => {
	const { token } = useAuth();

	const formFieldsArray = [
		[
			...(submode === "add"
				? [formFields.email({ required: true }), formFields.password({ required: true })]
				: [formFields.email({ required: submode === "add" })]),
		],
		formFields.appTheme(),
		formFields.isAdmin(),
	];
	const viewFieldsArray = [[viewFields.email(), viewFields.appTheme()], viewFields.isAdmin()];

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const customValidation = async (formData) => {
		const errors = {};
		const queryParams = { email: formData.email.trim() };
		const matches = await userApi.getAll(token, queryParams);
		const duplicates = matches.filter((existing) => {
			return data?.id !== existing.id;
		});
		console.log(duplicates);

		if (duplicates.length > 0) {
			errors.email = `A tag with this name already exists`;
		}
		return errors;
	};

	const transformFormData = (data) => {
		const transformed = {
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
			mode="formview"
			submode={submode}
			itemName="User"
			size={size}
			data={data || {}}
			fields={fields}
			endpoint={endpoint}
			onSuccess={onSuccess}
			onDelete={onDelete}
			validation={customValidation}
			transformFormData={transformFormData}
		/>
	);
};

export const UserFormModal = (props) => {
	const submode = props.isEdit || props.user?.id ? "edit" : "add";
	return <UserModal {...props} submode={submode} />;
};

export const UserViewModal = (props) => <UserModal {...props} submode="view" />;
