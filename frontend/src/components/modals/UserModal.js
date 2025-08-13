import React from "react";
import GenericModal from "./GenericModal";
import { formFields } from "../rendering/FormRenders";
import { viewFields } from "../rendering/ViewRenders";
import { authApi, userApi } from "../../services/api";
import { useAuth } from "../../contexts/AuthContext";
import "../Auth/Login.css";

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
		[formFields.email({ required: submode === "add" }), formFields.password({ required: submode === "add" })],
		[formFields.appTheme(), formFields.isAdmin()],
	];

	const viewFieldsArray = [[viewFields.email(), viewFields.appTheme()], viewFields.isAdmin()];

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const customValidation = async (formData) => {
		const errors = {};

		try {
			const queryParams = { email: formData.email.trim() };
			const matches = (await userApi.getAll?.(token, queryParams)) || [];
			const duplicates = matches.filter((existing) => {
				return data?.id !== existing.id;
			});

			if (duplicates.length > 0) {
				errors.email = "A user with this email already exists";
			}
		} catch (error) {
			// If the API call fails, we'll let the backend handle validation
			console.warn("Could not validate email uniqueness:", error);
		}

		return errors;
	};

	const transformFormData = (data) => {
		const transformed = {
			email: data.email?.trim(),
			theme: data.theme?.trim() || "mixed-berry",
			is_admin: data.is_admin || false,
		};

		// Only include password if it's provided (for new users or updates)
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
			title="User"
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
