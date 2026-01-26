import React, { useEffect, useState } from "react";
import { Form } from "react-bootstrap";
import { renderFormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { ValidationErrors } from "../../components/DataModal/DataModal";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAuth } from "../../contexts/AuthContext";
import { ApiResponse } from "../../services/api/Base";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { UserQualification } from "../../services/schemas/Core";
import { userQualificationApi } from "../../services/api/Users";

interface QualificationFormData {
	qualification_id?: number;
	experience?: string;
	skills?: string;
	qualities?: string;
	education?: string;
	interests?: string;
}

export const QualificationsTab: React.FC = () => {
	const { token } = useAuth();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const [formData, setFormData] = useState<QualificationFormData>({
		qualification_id: undefined,
		experience: "",
		skills: "",
		qualities: "",
		education: "",
		interests: "",
	});
	const [errors, setErrors] = useState<ValidationErrors>({});
	const [submitting, setSubmitting] = useState(false);

	useEffect(() => {
		const fetchQualifications = async () => {
			if (!token) return;
			try {
				const response: ApiResponse<UserQualification> = await userQualificationApi.getLatest(token);
				const data = response.data;
				if (data) {
					setFormData({
						qualification_id: data.id,
						experience: data.experience || "",
						skills: data.skills || "",
						qualities: data.qualities || "",
						education: data.education || "",
						interests: data.interests || "",
					});
				}
			} catch (error) {
				console.error("Error fetching qualification:", error);
			}
		};
		fetchQualifications().then();
	}, [token]);

	const handleInputChange = (e: SyntheticEvent) => {
		const { name, value } = e.target;
		setFormData((prev) => ({ ...prev, [name]: value }));
		if (errors[name]) {
			setErrors((prev) => ({ ...prev, [name]: "" }));
		}
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!token) return;
		setSubmitting(true);

		try {
			const qualificationData = {
				id: formData.qualification_id,
				experience: formData.experience || null,
				skills: formData.skills || null,
				qualities: formData.qualities || null,
				education: formData.education || null,
				interests: formData.interests || null,
			};

			const apiResult: ApiResponse<UserQualification> = await userQualificationApi.upsert(
				qualificationData,
				token
			);
			formData.qualification_id = apiResult.data.id;
			showToastSuccess("Qualifications saved successfully.");
		} catch (error) {
			console.error("Error saving qualifications:", error);
			showToastError("Failed to save qualifications.");
		} finally {
			setSubmitting(false);
		}
	};

	const experienceField: ModalFormField = {
		name: "experience",
		type: "textarea",
		label: "Experience",
		placeholder: "Describe your work experience...",
		rows: 3,
	};

	const skillsField: ModalFormField = {
		name: "skills",
		type: "textarea",
		label: "Skills",
		placeholder: "List your skills...",
		rows: 3,
	};

	const qualitiesField: ModalFormField = {
		name: "qualities",
		type: "textarea",
		label: "Qualities",
		placeholder: "Describe your qualities...",
		rows: 3,
	};

	const educationField: ModalFormField = {
		name: "education",
		type: "textarea",
		label: "Education",
		placeholder: "Describe your education...",
		rows: 3,
	};

	const interestsField: ModalFormField = {
		name: "interests",
		type: "textarea",
		label: "Interests",
		placeholder: "Describe your interests...",
		rows: 3,
	};

	return (
		<Form onSubmit={handleSubmit}>
			<p className="text-muted mb-4">
				Help us match you with the right opportunities by providing your qualifications
			</p>
			{renderFormField(experienceField, formData, handleInputChange, errors)}
			{renderFormField(skillsField, formData, handleInputChange, errors)}
			{renderFormField(qualitiesField, formData, handleInputChange, errors)}
			{renderFormField(educationField, formData, handleInputChange, errors)}
			{renderFormField(interestsField, formData, handleInputChange, errors)}

			<div className="mt-4">
				<ActionButton
					type="submit"
					variant="primary"
					disabled={submitting}
					defaultIcon="save"
					id={"confirm-button"}
					defaultText={submitting ? "Saving..." : "Save Qualifications"}
				/>
			</div>
		</Form>
	);
};
