const CARTO_API_KEY: string = import.meta.env.VITE_CARTO_API_KEY || "";

// Unkeyed tile requests still resolve, so maps render in environments with no key configured
const KEY_PARAM: string = CARTO_API_KEY ? `?key=${encodeURIComponent(CARTO_API_KEY)}` : "";

export const MAP_TILES = {
	light: `https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png${KEY_PARAM}`,
	dark: `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png${KEY_PARAM}`,
} as const;

export const MAP_ATTRIBUTION: string =
	'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>';
