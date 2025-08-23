import React from "react";
import GenericModal from "./GenericModal/GenericModal";
import { formFields, useCountries } from "../rendering/form/FormRenders";
import { viewFields } from "../rendering/view/ModalFieldRenders";
import { locationsApi } from "../../services/Api.ts";
import { useAuth } from "../../contexts/AuthContext";

export const LocationModal = ({
	show,
	onHide,
	data,
	onSuccess,
	onDelete,
	endpoint = "locations",
	submode = "view",
	size = "lg",
}) => {
	const { token } = useAuth();
	const { countries, loading: loadingCountries } = useCountries();

	let formFieldsArray = [];
	if (!data?.remote) {
		formFieldsArray = [formFields.city(), formFields.postcode(), formFields.country(countries, loadingCountries)];
	}

	// View fields for display
	let viewFieldsArray;
	if (!data?.remote) {
		viewFieldsArray = [[viewFields.city(), viewFields.postcode(), viewFields.country()], viewFields.locationMap()];
	} else {
		viewFieldsArray = [viewFields.locationMap({ label: "" })];
	}

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	const customValidation = async (formData) => {
		const errors = {};

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
			const queryParams = {};
			queryParams.city = (formData.city && formData.city.trim()) || null;
			queryParams.postcode = (formData.postcode && formData.postcode.trim()) || null;
			queryParams.country = (formData.country && formData.country.trim()) || null;
			const matchingLocations = await locationsApi.getAll(token, queryParams);
			const duplicates = matchingLocations.filter((existingLocation) => {
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

	const transformFormData = (data) => {
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
			mode="formview"
			submode={submode}
			itemName="Location"
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

export const LocationFormModal = (props) => {
	const submode = props.isEdit || props.location?.id ? "edit" : "add";
	return <LocationModal {...props} submode={submode} />;
};

export const LocationViewModal = (props) => <LocationModal {...props} submode="view" />;
