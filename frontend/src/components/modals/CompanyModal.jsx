import React from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { companiesApi } from "../../services/Api.ts";
import { useAuth } from "../../contexts/AuthContext.tsx";

export const CompanyModal = ({
	show,
	onHide,
	data,
	id,
	onSuccess,
	onDelete,
	endpoint = "companies",
	submode = "view",
	size = "lg",
}) => {
	const { token } = useAuth();

	const fields = {
		form: [
			formFields.name({ required: true }),
			[formFields.url({ label: "Website URL" })],
			[formFields.description()],
		],
		view: [viewFields.name({ isTitle: true }), viewFields.url(), [viewFields.description()]],
	};

	const transformFormData = (data) => {
		return {
			name: data.name?.trim(),
			url: data.url?.trim() || null,
			description: data.description?.trim() || null,
		};
	};

	const customValidation = async (formData) => {
		const errors = {};
		if (!formData.name) {
			return errors;
		}
		const queryParams = { name: formData.name.trim() };
		const matches = await companiesApi.getAll(token, queryParams);
		const duplicates = matches.filter((existing) => {
			return data?.id !== existing.id;
		});

		if (duplicates.length > 0 && formData.name) {
			errors.name = `A company with this name already exists`;
		}

		return errors;
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="formview"
			submode={submode}
			itemName="Company"
			size={size}
			data={data || {}}
			id={id}
			fields={fields}
			endpoint={endpoint}
			onSuccess={onSuccess}
			onDelete={onDelete}
			transformFormData={transformFormData}
			validation={customValidation}
		/>
	);
};
