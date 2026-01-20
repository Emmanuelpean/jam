import React, { createContext, useContext, useState, useEffect, ReactNode, JSX } from "react";
import { useAuth } from "./AuthContext";
import { useGlobalToast } from "../hooks/useNotificationToast";

interface ThemeContextType {
	isDarkMode: boolean;
	handleDarkModeToggle: () => void;
}

type Mode = "light" | "dark";

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const getInitialTheme = (): boolean => {
	// Check for system preference
	const systemPreference = window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false;

	// Set the theme IMMEDIATELY to prevent flash
	const mode: Mode = systemPreference ? "dark" : "light";
	document.body.setAttribute("data-mode", mode);
	document.documentElement.setAttribute("data-mode", mode);
	document.documentElement.setAttribute("data-bs-theme", mode);

	return systemPreference;
};

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }): JSX.Element => {
	const { currentUser, updateCurrentUser } = useAuth();
	const { showToastError } = useGlobalToast();

	const [isDarkMode, setIsDarkMode] = useState<boolean>(() => getInitialTheme());

	// Sync with user preference when they log in or currentUser loads
	useEffect(() => {
		if (currentUser?.preferences?.dark_mode !== undefined) {
			setIsDarkMode(currentUser.preferences.dark_mode);
		} else if (!currentUser) {
			const saved: string | null = localStorage.getItem("darkMode");

			// Check if localStorage has a MANUAL override (stored as string "manual:true" or "manual:false")
			if (saved !== null && saved.startsWith('"manual:')) {
				const manualValue: boolean = saved.includes("true");
				setIsDarkMode(manualValue);
			} else {
				// Otherwise use system preference
				if (window.matchMedia) {
					const systemPreference: boolean = window.matchMedia(
						"(prefers-color-scheme: dark)"
					).matches;
					setIsDarkMode(systemPreference);
				}
			}
		}
	}, [currentUser]);

	// Listen for system theme changes when user is not logged in
	useEffect(() => {
		if (currentUser) {
			return;
		}

		const mediaQuery: MediaQueryList = window.matchMedia("(prefers-color-scheme: dark)");

		const handleChange = (e: MediaQueryListEvent) => {
			const saved: string | null = localStorage.getItem("darkMode");

			// Only ignore if it's a MANUAL override
			if (saved === null || !saved.startsWith('"manual:')) {
				setIsDarkMode(e.matches);
			}
		};

		mediaQuery.addEventListener("change", handleChange);
		return () => {
			mediaQuery.removeEventListener("change", handleChange);
		};
	}, [currentUser]);

	useEffect(() => {
		const mode: Mode = isDarkMode ? "dark" : "light";
		document.body.setAttribute("data-mode", mode);
		document.documentElement.setAttribute("data-mode", mode);
		document.documentElement.setAttribute("data-bs-theme", mode);
	}, [isDarkMode, currentUser]);

	const handleDarkModeToggle = (): void => {
		const newValue = !isDarkMode;
		setIsDarkMode(newValue);

		if (currentUser) {
			updateCurrentUser({ preferences: { dark_mode: newValue } }).catch((err) =>
				showToastError("Failed to update user preferences:", err)
			);
		} else {
			localStorage.setItem("darkMode", JSON.stringify(`manual:${newValue}`));
		}
	};

	return (
		<ThemeContext.Provider value={{ isDarkMode, handleDarkModeToggle }}>
			{children}
		</ThemeContext.Provider>
	);
};

export const useTheme = () => {
	const context = useContext(ThemeContext);
	if (!context) {
		throw new Error("useTheme must be used within ThemeProvider");
	}
	return context;
};
