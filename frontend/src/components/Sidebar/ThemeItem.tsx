import React, { CSSProperties } from "react";

export interface ThemeColor {
	start: string;
	mid: string;
	end: string;
}

export const getCurrentCSSColors = (): ThemeColor => {
	const computedStyle: CSSStyleDeclaration = getComputedStyle(document.documentElement);
	return {
		start: computedStyle.getPropertyValue("--primary-start").trim(),
		mid: computedStyle.getPropertyValue("--primary-mid").trim(),
		end: computedStyle.getPropertyValue("--primary-end").trim(),
	};
};

export const getThemeColors = (themeKey: string): ThemeColor => {
	const originalTheme: string | null = document.documentElement.getAttribute("data-theme");
	document.documentElement.setAttribute("data-theme", themeKey);
	const colors: ThemeColor = getCurrentCSSColors();
	if (originalTheme) {
		document.documentElement.setAttribute("data-theme", originalTheme);
	}
	return colors;
};

interface ThemeItemProps {
	themeKey: string;
	themeName: string;
	isActive: boolean;
	isHovered: boolean;
	onClick: () => void;
	onMouseEnter: () => void;
	onMouseLeave: () => void;
}

export const ThemeItem: React.FC<ThemeItemProps> = ({
	themeKey,
	themeName,
	isActive,
	isHovered,
	onClick,
	onMouseEnter,
	onMouseLeave,
}: ThemeItemProps): JSX.Element => {
	const colors: ThemeColor = getThemeColors(themeKey);

	const getItemStyle = (): CSSProperties => {
		const baseStyle: CSSProperties = {
			display: "flex",
			alignItems: "center",
			padding: "7.2px 10.8px",
			borderRadius: "5.4px",
			cursor: "pointer",
			transition: "background-color 0.2s ease, border-color 0.2s ease",
			backgroundColor: "transparent",
			border: "3px solid transparent",
		};

		if (isActive) {
			return {
				...baseStyle,
				border: "3px solid var(--primary-mid, red)",
			};
		}

		if (isHovered) {
			return {
				...baseStyle,
				backgroundColor: "var(--bs-border-color)",
			};
		}

		return baseStyle;
	};

	return (
		<div
			id={`${themeKey}-theme`}
			style={getItemStyle()}
			onClick={onClick}
			onMouseEnter={onMouseEnter}
			onMouseLeave={onMouseLeave}
		>
			<div style={{ display: "flex", alignItems: "center", marginRight: "7.2px" }}>
				{Object.values(colors).map((color: string, index: number) => (
					<div
						key={index}
						style={{
							backgroundColor: color,
							width: "9px",
							height: "9px",
							borderRadius: "50%",
							marginRight: index < 2 ? "2.7px" : "0",
						}}
					/>
				))}
			</div>
			<span className="fw-medium">{themeName}</span>
		</div>
	);
};
