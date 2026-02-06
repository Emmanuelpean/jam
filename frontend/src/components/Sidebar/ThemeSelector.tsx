import React, { useState, JSX } from "react";
import { Theme, THEMES } from "../../utils/Theme";
import { useAuth } from "../../contexts/AuthContext";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { ThemeItem } from "./ThemeItem";
import { DarkModeToggle } from "./DarkModeToggle";

interface ThemeSelectorProps {
	currentTheme: string;
	onThemeChange: () => void;
	isVisible: boolean;
}

export const ThemeSelector: React.FC<ThemeSelectorProps> = ({
	currentTheme,
	onThemeChange,
	isVisible,
}: ThemeSelectorProps): JSX.Element | null => {
	const [hoveredItem, setHoveredItem] = useState<string | null>(null);
	const { showToastError } = useGlobalToast();
	const { updateCurrentUser } = useAuth();

	const handleThemeChange = async (themeKey: string): Promise<void> => {
		try {
			await updateCurrentUser({ preferences: { theme: themeKey } });
		} catch (error) {
			showToastError("Failed to save theme preference.");
			console.error("Error saving theme:", error);
		}
		onThemeChange();
	};

	if (!isVisible) return null;

	return (
		<div className="theme-dropdown">
			<div className="fw-medium text-muted small mb-2 px-2">Themes</div>
			{THEMES.map(
				(theme: Theme): JSX.Element => (
					<ThemeItem
						themeKey={theme.key}
						themeName={theme.name}
						isActive={currentTheme === theme.key}
						isHovered={hoveredItem === theme.key}
						onClick={(): Promise<void> => handleThemeChange(theme.key)}
						onMouseEnter={(): void => setHoveredItem(theme.key)}
						onMouseLeave={(): void => setHoveredItem(null)}
					/>
				)
			)}
			<DarkModeToggle />
		</div>
	);
};
