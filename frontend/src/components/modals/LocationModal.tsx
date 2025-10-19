import React from "react";
import DataModal, { DataModalProps, ValidationErrors } from "./DataModal/DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { LocationData, LocationDataTransform } from "../../services/Schemas";
import { tableColumns } from "../rendering/view/TableColumns";
import { useFormOptions } from "../rendering/form/FormOptions";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";

export const LocationModal: React.FC<DataModalProps> = ({ show, onHide, data, submode = "view", size = "lg" }) => {
	const { countries } = useFormOptions(["countries"]);
	const dataContext: DataContextValue = useDataContext();

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
		modalViewFields.accordionJobTableLocation({ helpText: "List of jobs at this location." }),
		modalViewFields.accordionInterviewTable({
			columns: [tableColumns.date!(), tableColumns.job!(), tableColumns.type!(), tableColumns.note!()],
			helpText: "List of interviews at this location.",
		}),
	];

	const customValidation = async (formData: LocationData): Promise<ValidationErrors> => {
		const errors: ValidationErrors = {};

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
			const duplicates: LocationData[] = dataContext.locations.filter((location: LocationData): boolean => {
				const cityMatch: boolean = location.city?.trim().toLowerCase() === formData.city?.trim().toLowerCase();
				const postcodeMatch: boolean =
					location.postcode?.trim().toLowerCase() === formData.postcode?.trim().toLowerCase();
				const countryMatch: boolean =
					location.country?.trim().toLowerCase() === formData.country?.trim().toLowerCase();
				return cityMatch && postcodeMatch && countryMatch && formData?.id !== location.id;
			});

			if (duplicates.length > 0) {
				const duplicateName = duplicates[0]!.name;
				errors.city =
					errors.postcode =
					errors.country =
						`A location with these details already exists: "${duplicateName}"`;
			}
		}
		return errors;
	};

	const transformFormData = (data: LocationData): LocationDataTransform => {
		return {
			city: data.city?.trim() || null,
			postcode: data.postcode?.trim() || null,
			country: data.country?.trim() || null,
		};
	};

	return (
		<DataModal
			show={show}
			onHide={onHide}
			mode={submode}
			itemName="Location"
			size={size}
			data={data}
			additionalFields={additionalFields}
			fields={fields}
			endpoint="locations"
			validation={customValidation}
			transformFormData={transformFormData}
		/>
	);
};
