import React, { useState, JSX, useEffect, useRef } from "react";
import { Form } from "react-bootstrap";
import { renderFormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { ValidationErrors } from "../../components/DataModal/DataModal";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useFormOptions } from "../../components/rendering/form/FormOptions";
import { useAuth } from "../../contexts/AuthContext";
import { UpdateCurrentUserResponse } from "../../services/api/Users";
import { ApiResponse } from "../../services/api/Base";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { Theme, THEMES } from "../../utils/Theme";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { DarkModeToggle } from "../../components/Sidebar/DarkModeToggle";
import { ThemeItem } from "../../components/Sidebar/ThemeItem";

interface PreferencesFormData {
	default_currency: string;
}

export const PreferencesTab: React.FC = () => {
	const { currentUser, updateCurrentUser, token } = useAuth();
	const { currencyNames } = useFormOptions();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const [formData, setFormData] = useState<PreferencesFormData>(() => ({
		default_currency: currentUser?.preferences.default_currency || "",
	}));
	const [errors, setErrors] = useState<ValidationErrors>({});
	const [submitting, setSubmitting] = useState(false);
	const formInitialized = useRef(false);

	useEffect(() => {
		if (currentUser && !formInitialized.current) {
			formInitialized.current = true;
			setFormData({
				default_currency: currentUser.preferences.default_currency || "",
			});
		}
	}, [currentUser]);
	const [hoveredTheme, setHoveredTheme] = useState<string | null>(null);
	const currentTheme: string = currentUser?.preferences.theme || "default";

	const handleThemeChange = async (themeKey: string): Promise<void> => {
		try {
			await updateCurrentUser({ preferences: { theme: themeKey } });
		} catch (error) {
			showToastError("Failed to save theme preference.");
			console.error("Error saving theme:", error);
		}
	};

	const handleInputChange = (e: SyntheticEvent): void => {
		const { name, value } = e.target;
		setFormData((prev: PreferencesFormData): PreferencesFormData => ({ ...prev, [name]: value }));
		if (errors[name]) {
			setErrors((prev: ValidationErrors): ValidationErrors => ({ ...prev, [name]: "" }));
		}
	};

	const handleSubmit = async (e: React.FormEvent): Promise<void> => {
		e.preventDefault();
		if (!token) return;
		setSubmitting(true);

		try {
			const response: ApiResponse<UpdateCurrentUserResponse> | null = await updateCurrentUser({
				preferences: { default_currency: formData.default_currency },
			});
			if (!response) return;

			showToastSuccess("Preferences updated successfully.");
		} catch (error) {
			showToastError("Failed to update preferences.");
		} finally {
			setSubmitting(false);
		}
	};

	const currencyField: ModalFormField = {
		key: "default_currency",
		type: "select",
		label: "Preferred Currency",
		options: currencyNames,
		isClearable: false,
	};

	return (
		<Form onSubmit={handleSubmit}>
			<h5 className="mb-3">
				<i className="bi bi-currency-dollar"></i> Currency Settings
			</h5>
			{renderFormField(currencyField, formData, handleInputChange, errors)}
			<hr className="my-4" />
			<h5 className="mb-3">
				<i className="bi bi-palette"></i> Appearance
			</h5>
			<p>
				Hint: You can also easily change the app theme and mode on the fly by clicking on the JAM logo in the
				sidebar.
			</p>
			<div className="mb-3">
				<label className="form-label">Theme</label>
				<div className="d-flex flex-wrap gap-2">
					{THEMES.map(
						(theme: Theme): JSX.Element => (
							<ThemeItem
								key={theme.key}
								themeKey={theme.key}
								themeName={theme.name}
								isActive={currentTheme === theme.key}
								isHovered={hoveredTheme === theme.key}
								onClick={(): Promise<void> => handleThemeChange(theme.key)}
								onMouseEnter={(): void => setHoveredTheme(theme.key)}
								onMouseLeave={(): void => setHoveredTheme(null)}
							/>
						)
					)}
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
