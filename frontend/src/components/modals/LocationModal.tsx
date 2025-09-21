import React from "react";
import GenericModal, { DataModalProps } from "./GenericModal/GenericModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { locationsApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import { ValidationErrors } from "./GenericModal/GenericModal";
import { LocationData } from "../../services/Schemas";
import { tableColumns } from "../rendering/view/TableColumns";
import { useFormOptions } from "../rendering/form/FormOptions";

export const LocationModal: React.FC<DataModalProps> = ({
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
	const { countries } = useFormOptions(["countries"]);

	const formFieldsArray = [
		formFields.city({ placeholder: "Oxford" }),
		formFields.postcode({ placeholder: "OX1 1AA" }),
		formFields.country(countries),
	];
	const viewFieldsArray = [
		[modalViewFields.city(), modalViewFields.postcode(), modalViewFields.country()],
		modalViewFields.locationMap(),
	];

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const additionalFields = [
		modalViewFields.accordionJobTable({ helpText: "List of jobs at this location." }),
		modalViewFields.accordionInterviewTable({
			columns: [tableColumns.date!(), tableColumns.job!(), tableColumns.type!(), tableColumns.note!()],
			helpText: "List of interviews at this location.",
		}),
	];

	const customValidation = async (formData: LocationData): Promise<ValidationErrors> => {
		const errors: ValidationErrors = {};
		if (!token) {
			return errors;
		}

		// Check if any value has been set
		const hasCity = formData.city && formData.city.trim();
		const hasPostcode = formData.postcode && formData.postcode.trim();
		const hasCountry = formData.country && formData.country.trim();
		const hasAnyValue = hasCity || hasPostcode || hasCountry;
		if (!hasAnyValue) {
			errors.city =
				errors.country =
				errors.postcode =
					"Please fill in at least one field (city, postcode, or country)";
		}

		// Check if the location already exist
		if (Object.keys(errors).length === 0) {
			const queryParams: Partial<LocationData> = {};
			queryParams.city = (formData.city && formData.city.trim()) || null;
			queryParams.postcode = (formData.postcode && formData.postcode.trim()) || null;
			queryParams.country = (formData.country && formData.country.trim()) || null;
			const matchingLocations = await locationsApi.getAll(token, queryParams);
			const duplicates = matchingLocations.filter((existingLocation: LocationData) => {
				return data?.id !== existingLocation.id;
			});

			if (duplicates.length > 0) {
				const duplicateName = duplicates[0].name;
				errors.city =
					errors.postcode =
					errors.country =
						`A location with these details already exists: "${duplicateName}"`;
			}
		}
		return errors;
	};

	const transformFormData = (data: LocationData) => {
		return {
			city: data.city?.trim() || null,
			postcode: data.postcode?.trim() || null,
			country: data.country?.trim() || null,
		};
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode={submode}
			itemName="Location"
			size={size}
			data={data}
			additionalFields={additionalFields}
			id={id}
			fields={fields}
			endpoint="locations"
			onSuccess={onSuccess}
			onDelete={onDelete}
			validation={customValidation}
			transformFormData={transformFormData}
		/>
	);
};
