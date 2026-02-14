import React, { useEffect, useState, JSX } from "react";
import { Card, Form } from "react-bootstrap";
import { renderFormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { ValidationErrors } from "../../components/DataModal/DataModal";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAuth } from "../../contexts/AuthContext";
import { useDataContext } from "../../contexts/DataContext";
import { ApiResponse } from "../../services/api/Base";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import LoadingSpinner from "../../components/Spinner/Spinner";
import { UserQualification } from "../../services/schemas/Core";
import { userQualificationApi } from "../../services/api/Users";
import { AiSystemPromptData } from "../../services/schemas/Services";

interface QualificationFormData {
	qualification_id?: number;
	experience?: string;
	skills?: string;
	qualities?: string;
	education?: string;
	interests?: string;
}

export const QualificationsTab: React.FC = (): JSX.Element => {
	const { token } = useAuth();
	const { aiSystemPrompts } = useDataContext();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const [formData, setFormData] = useState<QualificationFormData>({
		qualification_id: undefined,
		experience: "",
		skills: "",
		qualities: "",
		education: "",
		interests: "",
	});
	const [errors, _setErrors] = useState<ValidationErrors>({});
	const [loading, setLoading] = useState(true);
	const [submitting, setSubmitting] = useState(false);

	useEffect(() => {
		const fetchQualifications = async (): Promise<void> => {
			if (!token) return;
			try {
				const response: ApiResponse<UserQualification> = await userQualificationApi.getLatest(token);
				const data: UserQualification = response.data;
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
			} finally {
				setLoading(false);
			}
		};
		fetchQualifications().then();
	}, [token]);

	const handleInputChange = (e: SyntheticEvent): void => {
		const { name, value } = e.target;
		setFormData((prev: QualificationFormData): QualificationFormData => ({ ...prev, [name]: value }));
	};

	const handleSubmit = async (e: React.FormEvent): Promise<void> => {
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

	const EXPERIENCE_CHAR_LIMIT = 10000;
	const OTHER_CHAR_LIMIT = 3500;

	const experienceField: ModalFormField = {
		name: "experience",
		type: "textarea",
		label: "Experience",
		placeholder: "Describe your work experience...",
		rows: 3,
		autoHeight: true,
		maxChars: EXPERIENCE_CHAR_LIMIT,
	};

	const skillsField: ModalFormField = {
		name: "skills",
		type: "textarea",
		label: "Skills",
		placeholder: "List your skills...",
		rows: 3,
		autoHeight: true,
		maxChars: OTHER_CHAR_LIMIT,
	};

	const qualitiesField: ModalFormField = {
		name: "qualities",
		type: "textarea",
		label: "Qualities",
		placeholder: "Describe your qualities...",
		rows: 3,
		autoHeight: true,
		maxChars: OTHER_CHAR_LIMIT,
	};

	const educationField: ModalFormField = {
		name: "education",
		type: "textarea",
		label: "Education",
		placeholder: "Describe your education...",
		rows: 3,
		autoHeight: true,
		maxChars: OTHER_CHAR_LIMIT,
	};

	const interestsField: ModalFormField = {
		name: "interests",
		type: "textarea",
		label: "Interests",
		placeholder: "Describe your interests...",
		rows: 3,
		autoHeight: true,
		maxChars: OTHER_CHAR_LIMIT,
	};

	const latestSystemPrompt: AiSystemPromptData | null | undefined = aiSystemPrompts?.length
		? [...aiSystemPrompts].sort((a: AiSystemPromptData, b: AiSystemPromptData): number => b.id - a.id)[0]
		: null;
	const systemPrompt: string | undefined = latestSystemPrompt?.prompt;

	const hasAtLeastOneQualification: boolean =
		!!formData.experience?.trim() ||
		!!formData.skills?.trim() ||
		!!formData.qualities?.trim() ||
		!!formData.education?.trim() ||
		!!formData.interests?.trim();

	const isWithinCharLimits: boolean =
		(formData.experience?.length || 0) <= EXPERIENCE_CHAR_LIMIT &&
		(formData.skills?.length || 0) <= OTHER_CHAR_LIMIT &&
		(formData.qualities?.length || 0) <= OTHER_CHAR_LIMIT &&
		(formData.education?.length || 0) <= OTHER_CHAR_LIMIT &&
		(formData.interests?.length || 0) <= OTHER_CHAR_LIMIT;

	if (loading) {
		return <LoadingSpinner text="Loading qualifications..." />;
	}

	return (
		<>
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
						disabled={submitting || !hasAtLeastOneQualification || !isWithinCharLimits}
						defaultIcon="save"
						id={"confirm-button"}
						defaultText={submitting ? "Saving..." : "Save Qualifications"}
					/>
				</div>
			</Form>

			{systemPrompt && (
				<Card className="mt-4">
					<Card.Header>
						<i className="bi bi-robot me-2" />
						AI System Prompt
					</Card.Header>
					<Card.Body>
						<p className="text-muted mb-2">
							This is the system prompt used by the AI to evaluate job matches based on your
							qualifications.
						</p>
						<pre
							style={{
								whiteSpace: "pre-wrap",
								wordBreak: "break-word",
								backgroundColor: "var(--bs-tertiary-bg)",
								padding: "1rem",
								borderRadius: "0.375rem",
								fontSize: "0.875rem",
								margin: 0,
							}}
						>
							{systemPrompt}
						</pre>
					</Card.Body>
				</Card>
			)}
		</>
	);
};