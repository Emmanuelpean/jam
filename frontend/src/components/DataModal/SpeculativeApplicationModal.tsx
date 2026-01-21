import React, { forwardRef, useRef } from "react";
import DataModal, { DataModalHandle, DataModalProps, Fields, ValidationErrors } from "./DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import { useFormOptions } from "../rendering/form/FormOptions";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { CompanyModal } from "./CompanyModal";
import { PersonModal } from "./PersonModal";
import { SpeculativeApplicationData, SpeculativeApplicationDataTransform } from "../../services/schemas/DataTables";

export const SpeculativeApplicationModal = forwardRef<DataModalHandle, DataModalProps>(
	({ size = "lg" }: DataModalProps, ref) => {
		const personModalRef = useRef<DataModalHandle>(null);
		const companyModalRef = useRef<DataModalHandle>(null);
		const dataContext: DataContextValue = useDataContext();
		const { companies, persons } = useFormOptions();

		const jobFormFields: Fields = [
			[
				formFields.datetime({ required: false }),
				formFields.company(companies, companyModalRef, null, null, { required: true }),
			],
			[formFields.email({ name: "contact_email" }), formFields.contacts(persons, personModalRef)],
			formFields.note(),
		];

		const jobViewFields: Fields = [
			[modalViewFields.companyBadge(), modalViewFields.datetime()],
			[modalViewFields.contactEmail(), modalViewFields.personBadges({ key: "contacts" }, ["view", "edit", "delete"])],
			modalViewFields.note(),
		];

		const transformData = (formData: SpeculativeApplicationDataTransform): SpeculativeApplicationDataTransform => {
			return {
				date: formData.date ? new Date(formData.date) : null,
				note: formData.note?.trim() || null,
				contact_email: formData.contact_email?.trim() || null,
				company_id: formData.company_id,
				contacts: formData.contacts || [],
			};
		};

		const customValidation = async (formData: SpeculativeApplicationData): Promise<ValidationErrors> => {
			const errors: ValidationErrors = {};

			if (formData.company_id) {
				const urlDuplicates: SpeculativeApplicationData[] = dataContext.speculativeApplications.filter(
					(application: SpeculativeApplicationData): boolean => {
						return application.company_id === formData.company_id && application.id !== formData?.id;
					}
				);
				if (urlDuplicates.length > 0) {
					errors.company_id = `A Speculative Application for this company already exists`;
				}
			}
			return errors;
		};

		return (
			<>
				<DataModal
					ref={ref}
					transformFormData={transformData}
					entityType="speculativeApplication"
					size={size}
					fields={{
						form: jobFormFields,
						view: jobViewFields,
					}}
					validation={customValidation}
				/>

				<CompanyModal ref={companyModalRef} />
				<PersonModal ref={personModalRef} />
			</>
		);
	}
);
