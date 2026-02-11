import React, { createContext, JSX, ReactNode, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "./AuthContext";
import { useGlobalToast } from "../hooks/useNotificationToast";
import { ThemeMode } from "../services/schemas/Core";

interface ThemeContextType {
	themeMode: ThemeMode;
	isDarkMode: boolean;
	setThemeMode: (mode: ThemeMode) => void;
}

type AppliedMode = "light" | "dark";

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const getSystemPreference = (): boolean => window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false;

const applyMode = (mode: AppliedMode): void => {
	document.body.setAttribute("data-mode", mode);
	document.documentElement.setAttribute("data-mode", mode);
	document.documentElement.setAttribute("data-bs-theme", mode);
};

const getInitialThemeMode = (): ThemeMode => {
	// On initial load, default to system so there's no flash
	applyMode(getSystemPreference() ? "dark" : "light");
	return "system";
};

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }): JSX.Element => {
	const { currentUser, updateCurrentUser } = useAuth();
	const { showToastError } = useGlobalToast();

	const [themeMode, setThemeModeState] = useState<ThemeMode>(() => getInitialThemeMode());
	const [systemIsDark, setSystemIsDark] = useState<boolean>(() => getSystemPreference());

	// Listen for OS theme changes
	useEffect(() => {
		const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
		const handler = (e: MediaQueryListEvent) => setSystemIsDark(e.matches);
		mediaQuery.addEventListener("change", handler);
		return () => mediaQuery.removeEventListener("change", handler);
	}, []);

	// Sync with user preference when they log in or currentUser loads
	useEffect(() => {
		if (currentUser?.preferences?.dark_mode) {
			setThemeModeState(currentUser.preferences.dark_mode);
		} else if (!currentUser) {
			const saved: string | null = localStorage.getItem("themeMode");
			if (saved === "dark" || saved === "light" || saved === "system") {
				setThemeModeState(saved);
			} else {
				setThemeModeState("system");
			}
		}
	}, [currentUser]);

	// Derive the actual dark mode boolean
	const isDarkMode: boolean = useMemo((): boolean => {
		if (themeMode === "system") return systemIsDark;
		return themeMode === "dark";
	}, [themeMode, systemIsDark]);

	// Apply CSS attributes whenever isDarkMode changes
	useEffect((): void => {
		applyMode(isDarkMode ? "dark" : "light");
	}, [isDarkMode]);

	const setThemeMode = (mode: ThemeMode): void => {
		setThemeModeState(mode);

		if (currentUser) {
			updateCurrentUser({ preferences: { dark_mode: mode } }).catch((err) =>
				showToastError("Failed to update user preferences:", err)
			);
		} else {
			localStorage.setItem("themeMode", mode);
		}
	};

	return <ThemeContext.Provider value={{ themeMode, isDarkMode, setThemeMode }}>{children}</ThemeContext.Provider>;
};

export const useTheme = () => {
	const context = useContext(ThemeContext);
	if (!context) {
		throw new Error("useTheme must be used within ThemeProvider");
	}
	return context;
};
