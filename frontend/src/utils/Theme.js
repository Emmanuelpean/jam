export const THEMES = [
	{ key: "strawberry", name: "Strawberry" },
	{ key: "blueberry", name: "Blueberry" },
	{ key: "raspberry", name: "Raspberry" },
	{ key: "mixed-berry", name: "Mixed Berry" },
	{ key: "forest-berry", name: "Forest Berry" },
	{ key: "blackberry", name: "Blackberry" },
];

export const DEFAULT_THEME = "mixed-berry";

export const isValidTheme = (themeKey) => {
	return THEMES.some((theme) => theme.key === themeKey);
};

export const getThemeByKey = (themeKey) => {
	return THEMES.find((theme) => theme.key === themeKey);
};
