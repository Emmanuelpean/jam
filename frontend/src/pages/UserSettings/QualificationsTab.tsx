import React, { useEffect, useState } from "react";
import { Card, Form } from "react-bootstrap";
import { FormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { ValidationErrors } from "../../components/modals/DataModal/DataModal";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAuth } from "../../contexts/AuthContext";
import { ApiResponse } from "../../services/api/Base";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { UserQualification } from "../../services/Schemas";
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
		fetchQualifications();
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

			await userQualificationApi.upsert(qualificationData, token);
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
			{FormField(experienceField, formData, handleInputChange, errors)}
			{FormField(skillsField, formData, handleInputChange, errors)}
			{FormField(qualitiesField, formData, handleInputChange, errors)}
			{FormField(educationField, formData, handleInputChange, errors)}
			{FormField(interestsField, formData, handleInputChange, errors)}

			<div className="mt-4">
				<ActionButton
					type="submit"
					variant="primary"
					disabled={submitting}
					defaultIcon="save"
					defaultText={submitting ? "Saving..." : "Save Qualifications"}
				/>
			</div>
		</Form>
	);
};
