import React, { useEffect, useState, useMemo } from "react";
import { Dropdown } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { authApi } from "../../services/api";
import "./ThemeToggle.css";

const ThemeToggle = () => {
	const { token } = useAuth();

	// Move themes to a constant outside component to prevent recreation
	const themes = useMemo(
		() => [
			{ key: "strawberry", name: "Strawberry", description: "Sweet and vibrant" },
			{ key: "blueberry", name: "Blueberry", description: "Deep and rich" },
			{ key: "raspberry", name: "Raspberry", description: "Tart and bold" },
			{ key: "mixed-berry", name: "Mixed Berry", description: "Complex and layered" },
			{ key: "forest-berry", name: "Forest Berry", description: "Natural and earthy" },
			{ key: "blackberry", name: "Blackberry", description: "Deep and sophisticated" },
		],
		[],
	);

	const getInitialTheme = () => {
		const savedTheme = localStorage.getItem("theme");
		return savedTheme && themes.some((theme) => theme.key === savedTheme) ? savedTheme : "mixed-berry";
	};

	const [currentTheme, setCurrentTheme] = useState(getInitialTheme);

	const getCurrentCSSColors = () => {
		const computedStyle = getComputedStyle(document.documentElement);
		return {
			start: computedStyle.getPropertyValue("--primary-start").trim(),
			mid: computedStyle.getPropertyValue("--primary-mid").trim(),
			end: computedStyle.getPropertyValue("--primary-end").trim(),
		};
	};

	const applyTheme = (themeKey) => {
		document.documentElement.setAttribute("data-theme", themeKey);
	};

	const fetchUserTheme = async () => {
		if (!token) return null;

		try {
			const userData = await authApi.getCurrentUser(token);
			if (userData.theme && themes.find((theme) => theme.key === userData.theme)) {
				return userData.theme;
			}
		} catch (error) {
			console.error("Error fetching user theme:", error);
		}
		return null;
	};

	const saveThemeToDatabase = async (themeKey) => {
		// Always save to localStorage first
		localStorage.setItem("theme", themeKey);

		console.log("Saving theme to database:", themeKey);
		console.log("Token available:", !!token);

		if (!token) {
			console.log("No token available, skipping database save");
			return;
		}

		try {
			console.log("Calling updateUserTheme API...");
			const result = await authApi.updateUserTheme(themeKey, token);
			console.log("Theme saved successfully:", result);
		} catch (error) {
			console.error("Error saving theme:", error);
			// Log more details about the error
			console.error("Error details:", error.response?.data || error.message);
		}
	};


	// Initialize theme on mount
	useEffect(() => {
		applyTheme(currentTheme);
	}, []);

	// Sync with database when token changes
	useEffect(() => {
		if (!token) return;

		const syncWithDatabase = async () => {
			const dbTheme = await fetchUserTheme();
			if (dbTheme && dbTheme !== currentTheme) {
				setCurrentTheme(dbTheme);
				applyTheme(dbTheme);
				localStorage.setItem("theme", dbTheme);
			}
		};

		syncWithDatabase();
	}, [token]);


	// Apply theme when it changes
	useEffect(() => {
		applyTheme(currentTheme);
	}, [currentTheme]);

	const handleThemeChange = async (themeKey) => {
		setCurrentTheme(themeKey);
		await saveThemeToDatabase(themeKey);
	};

	const getThemeColors = (themeKey) => {
		const originalTheme = document.documentElement.getAttribute("data-theme");
		document.documentElement.setAttribute("data-theme", themeKey);
		const colors = getCurrentCSSColors();
		if (originalTheme) {
			document.documentElement.setAttribute("data-theme", originalTheme);
		}
		return colors;
	};

	const renderColorPreview = (colors) => (
		<div className="d-flex align-items-center me-2 theme-toggle-dot-container">
			{Object.values(colors).map((color, index) => (
				<div key={index} className="theme-toggle-dot" style={{ backgroundColor: color }} />
			))}
		</div>
	);

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