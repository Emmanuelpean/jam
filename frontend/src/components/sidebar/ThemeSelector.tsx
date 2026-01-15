import React, { useState } from "react";
import { THEMES } from "../../utils/Theme";
import { useAuth } from "../../contexts/AuthContext";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { DarkModeToggle } from "./DarkModeToggle";

interface ThemeSelectorProps {
	currentTheme: string;
	onThemeChange: () => void;
	isVisible: boolean;
}

interface CSSColors {
	start: string;
	mid: string;
	end: string;
}

export const ThemeSelector: React.FC<ThemeSelectorProps> = ({
	currentTheme,
	onThemeChange,
	isVisible,
}: ThemeSelectorProps) => {
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

	const getCurrentCSSColors = (): CSSColors => {
		const computedStyle: CSSStyleDeclaration = getComputedStyle(document.documentElement);
		return {
			start: computedStyle.getPropertyValue("--primary-start").trim(),
			mid: computedStyle.getPropertyValue("--primary-mid").trim(),
			end: computedStyle.getPropertyValue("--primary-end").trim(),
		};
	};

	const getThemeColors = (themeKey: string): CSSColors => {
		const originalTheme: string | null = document.documentElement.getAttribute("data-theme");
		document.documentElement.setAttribute("data-theme", themeKey);
		const colors: CSSColors = getCurrentCSSColors();
		if (originalTheme) {
			document.documentElement.setAttribute("data-theme", originalTheme);
		}
		return colors;
	};

	const renderColorPreview = (colors: CSSColors) => (
		<div style={{ display: "flex", alignItems: "center", marginRight: "8px" }}>
			{Object.values(colors).map((color, index) => (
				<div
					key={index}
					style={{
						backgroundColor: color,
						width: "10px",
						height: "10px",
						borderRadius: "50%",
						marginRight: index < 2 ? "3px" : "0",
					}}
				/>
			))}
		</div>
	);

	const getDropdownItemStyle = (itemKey: string, isActive: boolean): React.CSSProperties => {
		const baseStyle: React.CSSProperties = {
			display: "flex",
			alignItems: "center",
			padding: "8px 12px",
			borderRadius: "6px",
			cursor: "pointer",
			transition: "background-color 0.2s ease",
			backgroundColor: "transparent",
		};

		if (isActive) {
			return {
				...baseStyle,
				backgroundColor: "var(--bs-primary, #0d6efd)",
				color: "white",
			};
		}

		if (hoveredItem === itemKey) {
			return {
				...baseStyle,
				backgroundColor: "var(--bs-border-color)",
			};
		}

		return baseStyle;
	};

	if (!isVisible) return null;

	return (
		<div className="theme-dropdown">
			<div className="fw-medium text-muted small mb-2 px-2">Themes</div>
			{THEMES.map((theme) => {
				const previewColors = getThemeColors(theme.key);
				const isCurrentTheme = currentTheme === theme.key;
				return (
					<div
						key={theme.key}
						style={getDropdownItemStyle(theme.key, isCurrentTheme)}
						onClick={() => handleThemeChange(theme.key)}
						onMouseEnter={() => setHoveredItem(theme.key)}
						onMouseLeave={() => setHoveredItem(null)}
					>
						{renderColorPreview(previewColors)}
						<div>
							<div className="fw-medium">{theme.name}</div>
						</div>
					</div>
				);
			})}
			<DarkModeToggle />
		</div>
	);
};
