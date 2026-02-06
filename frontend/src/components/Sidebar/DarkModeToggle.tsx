import React from "react";
import "./DarkModeToggle.scss";
import { useTheme } from "../../contexts/ThemeContext";

export const DarkModeToggle: React.FC = () => {
	const { isDarkMode, handleDarkModeToggle } = useTheme();

	return (
		<div className="dark-mode-toggle-container" id={"theme-switch-div"}>
			<label className="dark-mode-toggle" htmlFor="theme-switch" id={"theme-switch-label"}>
				<input
					type="checkbox"
					id="theme-switch"
					checked={isDarkMode}
					onChange={handleDarkModeToggle}
					aria-label="Toggle dark mode"
				/>
				<span className="slider">
					<i className="bi bi-sun-fill sun-icon"></i>
					<i className="bi bi-moon-stars-fill moon-icon"></i>
				</span>
				<span className="toggle-label">{isDarkMode ? "Dark" : "Light"} Mode</span>
			</label>
		</div>
	);
};
