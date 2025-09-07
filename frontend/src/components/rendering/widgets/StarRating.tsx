import React, { JSX, useState } from "react";
import "./StarRating.css";
import { SyntheticEvent, WidgetProps } from "./WidgetRenders";

const StarRating = ({ field, value, handleChange }: WidgetProps): JSX.Element => {
	const [hoverRating, setHoverRating] = useState<number>(0);
	const maxRating = field.maxRating || 5;
	const currentRating = parseInt(String(value)) || 0;

	const handleStarClick = (rating: number): void => {
		const syntheticEvent: SyntheticEvent = {
			target: {
				name: field.name,
				value: rating === currentRating ? 0 : rating,
			},
		};
		handleChange(syntheticEvent);
	};

	const handleStarHover = (rating: number): void => {
		setHoverRating(rating);
	};

	const handleMouseLeave = (): void => {
		setHoverRating(0);
	};

	const getStarClass = (starNumber: number): string => {
		const rating = hoverRating || currentRating;
		if (starNumber <= rating) {
			return "bi-star-fill";
		}
		return "bi-star";
	};

	return (
		<>
			<div className="star-rating-container">
				<div className="star-rating-stars" onMouseLeave={handleMouseLeave}>
					{[...Array(maxRating)].map((_, index) => {
						const starNumber = index + 1;
						return (
							<i
								key={starNumber}
								className={`star-rating-star ${getStarClass(starNumber)}`}
								onMouseEnter={() => handleStarHover(starNumber)}
								onClick={() => handleStarClick(starNumber)}
							/>
						);
					})}
				</div>
			</div>
		</>
	);
};

export const renderStarRating = ({ field, value, handleChange }: WidgetProps): JSX.Element => {
	return <StarRating field={field} value={value} handleChange={handleChange} />;
};
