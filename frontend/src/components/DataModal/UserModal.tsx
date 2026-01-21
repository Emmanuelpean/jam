import React, { forwardRef, JSX } from "react";
import DataModal, { DataModalHandle, Fields, JamDataModalProps, ValidationErrors } from "./DataModal";
import { formFields } from "../rendering/form/FormRenders";
import { modalViewFields } from "../rendering/view/ModalFields";
import "../../pages/Auth/AuthPage.css";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { UserData, UserDataTransform } from "../../services/schemas/Core";

export const UserModal = forwardRef<DataModalHandle, JamDataModalProps>(
	({ size = "lg" }: JamDataModalProps, ref): JSX.Element => {
		const dataContext: DataContextValue = useDataContext();

		const createFields = (data: any, mode: string): { form: Fields; view: Fields } => {
			const isAddMode: boolean = mode === "add" || !data?.id;

			const formFieldsArray: Fields = [
				[formFields.email({ required: true }), ...(isAddMode ? [formFields.password({ required: true })] : [])],
				[formFields.isAdmin(), formFields.isActive()],
				[formFields.premiumActive(), formFields.jobScrapingActive(), formFields.jobRatingActive()],
			];

			const viewFieldsArray: Fields = [
				[modalViewFields.email(), modalViewFields.personName()],
				[modalViewFields.isAdmin(), modalViewFields.isActive()],
				[
					modalViewFields.premiumActive(),
					modalViewFields.jobScrapingActive(),
					modalViewFields.jobRatingActive(),
				],
			];

			return {
				form: formFieldsArray,
				view: viewFieldsArray,
			};
		};

		const customValidation = async (formData: UserData): Promise<ValidationErrors> => {
			const errors: ValidationErrors = {};
			const duplicates: UserData[] = dataContext.users.filter(
				(user: UserData): boolean =>
					user.email.trim().toLowerCase() === formData.email.trim().toLowerCase() && user.id !== formData?.id
			);
			if (duplicates.length > 0) {
				errors.email = `A user with this email address already exists`;
			}
			return errors;
		};

		const transformFormData = (formData: any): UserDataTransform => {
			return {
				email: formData.email?.trim(),
				password: formData.password?.trim(),
				is_admin: formData.is_admin || false,
				is_active: formData.is_active || false,
				premium: {
					is_active: formData.premium?.is_active || false,
					job_scraping_active: formData.premium?.job_scraping_active || false,
					job_rating_active: formData.premium?.job_rating_active || false,
				},
			};
		};

		return (
			<DataModal
				ref={ref}
				size={size}
				fields={createFields}
				entityType="user"
				validation={customValidation}
				transformFormData={transformFormData}
			/>
		);
	}
);
