import { createContext, useContext } from "react";
import { ThemeMode } from "../services/schemas/Core";

export interface ThemeContextType {
	themeMode: ThemeMode;
	isDarkMode: boolean;
	setThemeMode: (mode: ThemeMode) => void;
}

export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
	const context = useContext(ThemeContext);
	if (!context) {
		throw new Error("useTheme must be used within ThemeProvider");
	}
	return context;
};
