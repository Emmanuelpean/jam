import React, { JSX, useState } from "react";
import { SyntheticEvent, WidgetProps } from "./WidgetRenders";
import { toKey } from "../../../utils/StringUtils";

export const FavouriteStar = ({ field, value, handleChange }: WidgetProps): JSX.Element => {
	const isFavourite: boolean = Boolean(value);
	const [hovered, setHovered] = useState<boolean>(false);

	const handleClick = (): void => {
		const syntheticEvent: SyntheticEvent = {
			target: {
				name: toKey(field.name),
				value: !isFavourite,
				type: "checkbox",
				checked: !isFavourite,
			},
		};
		handleChange(syntheticEvent);
	};

	const active: boolean = isFavourite || hovered;

	return (
		<div style={{ display: "flex", height: "50px", minWidth: "250px" }}>
			<button
				type="button"
				onClick={handleClick}
				onMouseEnter={() => setHovered(true)}
				onMouseLeave={() => setHovered(false)}
				title={isFavourite ? "Remove from favourites" : "Mark as favourite"}
				style={{
					background: "none",
					border: "none",
					padding: "0.25rem",
					cursor: "pointer",
					lineHeight: 1,
					display: "flex",
					alignItems: "center",
				}}
			>
				<i
					className={`bi ${active ? "bi-star-fill" : "bi-star"}`}
					style={{
						fontSize: "1.75rem",
						color: active ? "#f5c518" : "var(--bs-secondary-color)",
						transition: "color 0.15s, transform 0.15s",
					}}
				/>
			</button>
		</div>
	);
};
