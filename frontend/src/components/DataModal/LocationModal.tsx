import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, Fields, JamDataModalProps, ValidationErrors } from "./DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { ModalViewField, modalViewFields } from "../rendering/view/ModalFields";
import { tableColumns } from "../rendering/view/TableColumns";
import { useFormOptions } from "../rendering/form/FormOptions";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { LocationData, LocationDataTransform } from "../../services/schemas/DataTables";

export const LocationModal = forwardRef<DataModalHandle<LocationData>, JamDataModalProps>(
	({ size = "lg" }: JamDataModalProps, ref): JSX.Element => {
		const { countries } = useFormOptions();
		const dataContext: DataContextValue = useDataContext();

		const formFieldsArray: Fields = [
			formFields.city({ placeholder: "Oxford" }),
			formFields.postcode({ placeholder: "OX1 1AA" }),
			formFields.country(countries),
		];
		const viewFieldsArray: Fields = [
			[modalViewFields.city(), modalViewFields.postcode(), modalViewFields.country()],
			modalViewFields.locationMap(),
		];

		const fields = {
			form: formFieldsArray,
			view: viewFieldsArray,
		};

		const additionalFields: ModalViewField[] = [
			modalViewFields.accordionJobTableLocation({
				helpText: "List of jobs at this location.",
			}),
			modalViewFields.accordionInterviewTable({
				columns: [
					tableColumns.dateColumn(),
					tableColumns.jobBadgeColumn(),
					tableColumns.typeColumn(),
					tableColumns.noteColumn(),
				],
				helpText: "Interviews at this location.",
			}),
		];

		const customValidation = async (formData: LocationData): Promise<ValidationErrors> => {
			const errors: ValidationErrors = {};

			// Check if any value has been set
			const hasCity: string | null | undefined = formData.city && formData.city.trim();
			const hasPostcode: string | null | undefined = formData.postcode && formData.postcode.trim();
			const hasCountry: string | null | undefined = formData.country && formData.country.trim();
			const hasAnyValue: boolean = !!(hasCity || hasPostcode || hasCountry);
			if (!hasAnyValue) {
				errors.city =
					errors.country =
					errors.postcode =
						"Please fill in at least one field (city, postcode, or country)";
			}

			// Check if the location already exists
			if (Object.keys(errors).length === 0) {
				const duplicates: LocationData[] = dataContext.locations.filter((location: LocationData): boolean => {
					const cityMatch: boolean =
						location.city?.trim().toLowerCase() === formData.city?.trim().toLowerCase();
					const postcodeMatch: boolean =
						location.postcode?.trim().toLowerCase() === formData.postcode?.trim().toLowerCase();
					const countryMatch: boolean =
						location.country?.trim().toLowerCase() === formData.country?.trim().toLowerCase();
					return cityMatch && postcodeMatch && countryMatch && formData?.id !== location.id;
				});

				if (duplicates.length > 0) {
					const duplicateName: string = duplicates[0]!.name;
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
			<DataModal<LocationData>
				ref={ref}
				size={size}
				additionalFields={additionalFields}
				fields={fields}
				entityType="location"
				validation={customValidation}
				transformFormData={transformFormData}
			/>
		);
	}
);
