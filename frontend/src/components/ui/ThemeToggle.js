import React, { useEffect, useState } from "react";
import { Dropdown } from "react-bootstrap";
import "./ThemeToggle.css";

const ThemeToggle = () => {
	const [currentTheme, setCurrentTheme] = useState("mixed-berry");
	const [currentColors, setCurrentColors] = useState({
		start: "#ffffff",
		mid: "#ffffff",
		end: "#ffffff",
	});

	const themes = [
		{
			key: "strawberry",
			name: "Strawberry",
			description: "Sweet and vibrant",
		},
		{
			key: "blueberry",
			name: "Blueberry",
			description: "Deep and rich",
		},
		{
			key: "raspberry",
			name: "Raspberry",
			description: "Tart and bold",
		},
		{
			key: "mixed-berry",
			name: "Mixed Berry",
			description: "Complex and layered",
		},
		{
			key: "forest-berry",
			name: "Forest Berry",
			description: "Natural and earthy",
		},
		{
			key: "blackberry",
			name: "Blackberry",
			description: "Deep and sophisticated",
		},
	];

	// Function to get current CSS variable values
	const getCurrentCSSColors = () => {
		const computedStyle = getComputedStyle(document.documentElement);
		return {
			start: computedStyle.getPropertyValue("--primary-start").trim(),
			mid: computedStyle.getPropertyValue("--primary-mid").trim(),
			end: computedStyle.getPropertyValue("--primary-end").trim(),
		};
	};

	// Apply theme and update colors
	useEffect(() => {
		document.documentElement.setAttribute("data-theme", currentTheme);

		// Store theme preference in localStorage
		localStorage.setItem("theme", currentTheme);

		// Update current colors from CSS variables after theme change
		// Use setTimeout to ensure CSS has been updated
		setTimeout(() => {
			setCurrentColors(getCurrentCSSColors());
		}, 10);
	}, [currentTheme]);

	// Load saved theme on component mount
	useEffect(() => {
		const savedTheme = localStorage.getItem("theme");
		if (savedTheme && themes.find((theme) => theme.key === savedTheme)) {
			setCurrentTheme(savedTheme);
		}
		setCurrentColors(getCurrentCSSColors());
	}, []);

	const handleThemeChange = (themeKey) => {
		setCurrentTheme(themeKey);
	};

	const getCurrentTheme = () => {
		return themes.find((theme) => theme.key === currentTheme);
	};

	const renderColorPreview = (colors) => (
		<div className="d-flex align-items-center me-2 theme-toggle-dot-container">
			<div className="theme-toggle-dot" style={{ backgroundColor: colors.start }} />
			<div className="theme-toggle-dot" style={{ backgroundColor: colors.mid }} />
			<div className="theme-toggle-dot" style={{ backgroundColor: colors.end }} />
		</div>
	);

	const getThemeColors = (themeKey) => {
		const originalTheme = document.documentElement.getAttribute("data-theme");
		document.documentElement.setAttribute("data-theme", themeKey);
		const colors = getCurrentCSSColors();
		document.documentElement.setAttribute("data-theme", originalTheme);
		return colors;
	};

	// noinspection JSValidateTypes
	return (
		<Dropdown>
			<Dropdown.Toggle className="theme-toggle-btn d-flex align-items-center">
				<span>JAM</span>
			</Dropdown.Toggle>
			<Dropdown.Menu>
				{themes.map((theme) => {
					const previewColors = getThemeColors(theme.key);

					return (
						<Dropdown.Item
							key={theme.key}
							onClick={() => handleThemeChange(theme.key)}
							active={currentTheme === theme.key}
							className="d-flex align-items-center py-2"
						>
							{renderColorPreview(previewColors)}
							<div>
								<div className="fw-medium theme-dropdown-item-text">{theme.name}</div>
							</div>
						</Dropdown.Item>
					);
				})}
			</Dropdown.Menu>
		</Dropdown>
	);
};

export default ThemeToggle;
