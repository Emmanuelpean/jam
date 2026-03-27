import React, { JSX } from "react";
import "./ClearButton.scss";

interface Props {
	onClick: () => void;
	ariaLabel?: string;
	size?: "sm" | "md";
}

const ClearButton = ({ onClick, ariaLabel = "Clear", size = "md" }: Props): JSX.Element => (
	<button
		type="button"
		className={`clear-btn clear-btn--${size}`}
		onClick={onClick}
		aria-label={ariaLabel}
		id={"clear-btn"}
	>
		<i className="bi-x-lg" />
	</button>
);

export default ClearButton;
