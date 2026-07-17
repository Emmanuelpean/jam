import React, { useState, JSX, useEffect, useRef } from "react";
import { Form } from "react-bootstrap";
import { renderFormField, SyntheticEvent } from "../../components/rendering/widgets/WidgetRenders";
import { ValidationErrors } from "../../components/DataModal/DataModal";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useFormOptions } from "../../components/rendering/form/FormOptions";
import { useAuth } from "../../contexts/AuthContext";
import { ModalFormField } from "../../components/rendering/form/FormRenders";
import { Theme, THEMES } from "../../utils/Theme";
import { DarkModeToggle } from "../../components/Sidebar/DarkModeToggle";
import { ThemeItem } from "../../components/Sidebar/ThemeItem";

interface PreferencesFormData {
	default_currency: string;
}

export const PreferencesTab: React.FC = () => {
	const { currentUser, updateCurrentUser } = useAuth();
	const { currencyNames } = useFormOptions();
	const { showToastError } = useGlobalToast();
	const [formData, setFormData] = useState<PreferencesFormData>(() => ({
		default_currency: currentUser?.preferences.default_currency || "",
	}));
	const [errors, setErrors] = useState<ValidationErrors>({});
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

	const tourPanelDismissed: boolean = currentUser?.preferences.tour_panel_dismissed ?? false;

	const handleTourShortcutToggle = async (e: React.ChangeEvent<HTMLInputElement>): Promise<void> => {
		try {
			await updateCurrentUser({ preferences: { tour_panel_dismissed: !e.target.checked } });
		} catch (error) {
			showToastError("Failed to update preferences.");
			console.error("Error saving tour preference:", error);
		}
	};

	const handleInputChange = async (e: SyntheticEvent): Promise<void> => {
		const { name, value } = e.target;
		setFormData((prev: PreferencesFormData): PreferencesFormData => ({ ...prev, [name]: value }));
		if (errors[name]) {
			setErrors((prev: ValidationErrors): ValidationErrors => ({ ...prev, [name]: "" }));
		}

		try {
			await updateCurrentUser({ preferences: { [name]: value } });
		} catch (error) {
			showToastError("Failed to update preferences.");
			console.error("Error saving preferences:", error);
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
		<Form>
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
			<hr className="my-4" />
			<h5 className="mb-3">
				<i className="bi bi-map"></i> Guided Tours
			</h5>
			<Form.Check
				type="switch"
				id="tour-shortcut-toggle"
				label="Show the &ldquo;Take a Tour&rdquo; shortcut in the sidebar"
				checked={!tourPanelDismissed}
				onChange={handleTourShortcutToggle}
			/>
			<Form.Text className="text-muted">
				The shortcut appears in the sidebar while there are tours left to take. You can always start a tour from
				the About page.
			</Form.Text>
		</Form>
	);
};
