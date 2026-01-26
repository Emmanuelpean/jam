import React, { useState } from "react";
import { Form } from "react-bootstrap";
import { rendFormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { ValidationErrors } from "../../components/DataModal/DataModal";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useFormOptions } from "../../components/rendering/form/FormOptions";
import { useAuth } from "../../contexts/AuthContext";
import { UpdateCurrentUserResponse } from "../../services/api/Users";
import { ApiResponse } from "../../services/api/Base";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { Theme, THEMES } from "../../utils/Theme";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { DarkModeToggle } from "../../components/sidebar/DarkModeToggle";
import { ThemeItem } from "../../components/sidebar/ThemeItem";

interface PreferencesFormData {
	default_currency: string;
	chase_threshold?: number;
	deadline_threshold?: number;
	update_limit?: number;
}

export const PreferencesTab: React.FC = () => {
	const { currentUser, updateCurrentUser, token } = useAuth();
	const { currencyNames } = useFormOptions();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const [formData, setFormData] = useState<PreferencesFormData>(() => ({
		default_currency: currentUser?.preferences.default_currency || "",
		chase_threshold: currentUser?.preferences.chase_threshold || 0,
		deadline_threshold: currentUser?.preferences.deadline_threshold || 0,
		update_limit: currentUser?.preferences.update_limit || 0,
	}));
	const [errors, setErrors] = useState<ValidationErrors>({});
	const [submitting, setSubmitting] = useState(false);
	const [hoveredTheme, setHoveredTheme] = useState<string | null>(null);
	const currentTheme = currentUser?.preferences.theme || "default";

	const handleThemeChange = async (themeKey: string): Promise<void> => {
		try {
			await updateCurrentUser({ preferences: { theme: themeKey } });
		} catch (error) {
			showToastError("Failed to save theme preference.");
			console.error("Error saving theme:", error);
		}
	};

	const handleInputChange = (e: SyntheticEvent) => {
		const { name, value } = e.target;
		setFormData((prev) => ({ ...prev, [name]: value }));
		if (errors[name]) {
			setErrors((prev) => ({ ...prev, [name]: "" }));
		}
	};

	const validateForm = (): boolean => {
		const newErrors: ValidationErrors = {};

		if (
			formData.chase_threshold !== undefined &&
			(formData.chase_threshold < 1 || formData.chase_threshold > 365)
		) {
			newErrors.chase_threshold = "Chase threshold must be between 1 and 365 days";
		}

		if (
			formData.deadline_threshold !== undefined &&
			(formData.deadline_threshold < 1 || formData.deadline_threshold > 365)
		) {
			newErrors.deadline_threshold = "Deadline threshold must be between 1 and 365 days";
		}

		if (formData.update_limit !== undefined && (formData.update_limit < 1 || formData.update_limit > 1000)) {
			newErrors.update_limit = "Update limit must be between 1 and 1000";
		}

		setErrors(newErrors);
		return Object.keys(newErrors).length === 0;
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!validateForm() || !token) return;
		setSubmitting(true);

		try {
			const updateData: any = { default_currency: formData.default_currency };
			if (formData.chase_threshold !== undefined) updateData.chase_threshold = formData.chase_threshold;
			if (formData.deadline_threshold !== undefined) updateData.deadline_threshold = formData.deadline_threshold;
			if (formData.update_limit !== undefined) updateData.update_limit = formData.update_limit;

			const response: ApiResponse<UpdateCurrentUserResponse> | null = await updateCurrentUser({
				preferences: updateData,
			});
			if (!response) return;

			showToastSuccess("Preferences updated successfully.");
		} catch (error) {
			showToastError("Failed to update preferences.");
		} finally {
			setSubmitting(false);
		}
	};

	const chaseThresholdField: ModalFormField = {
		name: "chase_threshold",
		type: "number",
		label: "Chase Threshold (days)",
		placeholder: "10",
		helpText: "Jobs below this threshold will be flagged for follow-up",
	};

	const deadlineThresholdField: ModalFormField = {
		name: "deadline_threshold",
		type: "number",
		label: "Deadline Threshold (days)",
		placeholder: "3",
		helpText: "Jobs within this threshold are considered near deadline",
	};

	const updateLimitField: ModalFormField = {
		name: "update_limit",
		type: "number",
		label: "Update Display Limit",
		placeholder: "50",
		helpText: "Maximum number of job updates to show",
	};

	const currencyField: ModalFormField = {
		name: "default_currency",
		type: "select",
		label: "Preferred Currency",
		options: currencyNames,
		isClearable: false,
	};

	return (
		<Form onSubmit={handleSubmit}>
			<h5 className="mb-3">
				<i className="bi bi-speedometer"></i> Dashboard Settings
			</h5>
			{rendFormField(chaseThresholdField, formData, handleInputChange, errors)}
			{rendFormField(deadlineThresholdField, formData, handleInputChange, errors)}
			{rendFormField(updateLimitField, formData, handleInputChange, errors)}
			<hr className="my-4" />
			<h5 className="mb-3">
				<i className="bi bi-currency-dollar"></i> Currency Settings
			</h5>
			{rendFormField(currencyField, formData, handleInputChange, errors)}
			<hr className="my-4" />
			<h5 className="mb-3">
				<i className="bi bi-palette"></i> Appearance
			</h5>
			<div className="mb-3">
				<label className="form-label">Theme</label>
				<div className="d-flex flex-wrap gap-2">
					{THEMES.map((theme: Theme) => (
						<ThemeItem
							key={theme.key}
							themeKey={theme.key}
							themeName={theme.name}
							isActive={currentTheme === theme.key}
							isHovered={hoveredTheme === theme.key}
							onClick={() => handleThemeChange(theme.key)}
							onMouseEnter={() => setHoveredTheme(theme.key)}
							onMouseLeave={() => setHoveredTheme(null)}
						/>
					))}
				</div>
			</div>
			<div className="mb-3">
				<label className="form-label">Mode</label>
				<DarkModeToggle />
			</div>
			<div className="mt-4">
				<ActionButton
					type="submit"
					variant="primary"
					disabled={submitting}
					defaultIcon="save"
					id={"confirm-button"}
					defaultText={submitting ? "Saving..." : "Save Preferences"}
				/>
			</div>
		</Form>
	);
};