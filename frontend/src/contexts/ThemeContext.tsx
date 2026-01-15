import React, { createContext, useContext, useState, useEffect, ReactNode, JSX } from "react";

interface ThemeContextType {
	isDarkMode: boolean;
	handleDarkModeToggle: () => void;
}

type Mode = "light" | "dark";

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }): JSX.Element => {
	const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
		const saved = localStorage.getItem("darkMode");
		return saved ? JSON.parse(saved) : false;
	});

	useEffect(() => {
		const mode: Mode = isDarkMode ? "dark" : "light";
		document.body.setAttribute("data-mode", mode);
		document.documentElement.setAttribute("data-mode", mode);
		document.documentElement.setAttribute("data-bs-theme", mode);
		localStorage.setItem("darkMode", JSON.stringify(isDarkMode));
	}, [isDarkMode]);

	const handleDarkModeToggle = (): void => {
		setIsDarkMode((prev: boolean): boolean => !prev);
	};

	return <ThemeContext.Provider value={{ isDarkMode, handleDarkModeToggle }}>{children}</ThemeContext.Provider>;
};

export const useTheme = () => {
	const context = useContext(ThemeContext);
	if (!context) {
		throw new Error("useTheme must be used within ThemeProvider");
	}
	return context;
};
