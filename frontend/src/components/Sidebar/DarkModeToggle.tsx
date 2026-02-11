import React from "react";
import "./DarkModeToggle.scss";
import { useTheme } from "../../contexts/ThemeContext";
import { ThemeMode } from "../../services/schemas/Core";

const options: { mode: ThemeMode; icon: string; label: string }[] = [
	{ mode: "light", icon: "bi-sun-fill", label: "Light" },
	{ mode: "system", icon: "bi-display", label: "Auto" },
	{ mode: "dark", icon: "bi-moon-stars-fill", label: "Dark" },
];

export const DarkModeToggle: React.FC = () => {
	const { themeMode, setThemeMode } = useTheme();

	const activeIndex = options.findIndex((o) => o.mode === themeMode);

	return (
		<div className="dark-mode-toggle-container" id="theme-switch-div">
			<div className="theme-segmented-control" role="radiogroup" aria-label="Theme mode">
				<div
					className="theme-segment-indicator"
					style={{ transform: `translateX(${activeIndex * 100}%)` }}
				/>
				{options.map(({ mode, icon, label }) => (
					<button
						key={mode}
						className={`theme-segment${themeMode === mode ? " active" : ""}`}
						onClick={() => setThemeMode(mode)}
						role="radio"
						aria-checked={themeMode === mode}
						aria-label={`${label} mode`}
						title={`${label} mode`}
					>
						<i className={`bi ${icon}`}></i>
						<span className="segment-label">{label}</span>
					</button>
				))}
			</div>
		</div>
	);
};
