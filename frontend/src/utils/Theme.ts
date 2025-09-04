export interface Theme {
	key: string;
	name: string;
}

export const THEMES: Theme[] = [
	{ key: "strawberry", name: "Strawberry" },
	{ key: "blueberry", name: "Blueberry" },
	{ key: "raspberry", name: "Raspberry" },
	{ key: "mixed-berry", name: "Mixed Berry" },
	{ key: "forest-berry", name: "Forest Berry" },
	{ key: "blackberry", name: "Blackberry" },
];

export const DEFAULT_THEME: string = "mixed-berry";

export const isValidTheme = (themeKey: string) => {
	return THEMES.some((theme: Theme): boolean => theme.key === themeKey);
};

export const getThemeByKey = (themeKey: string): Theme | undefined => {
	return THEMES.find((theme) => theme.key === themeKey);
};
