import React, { useState } from "react";
import "./HelpBubble.css";

interface HelpBubbleProps {
	helpText: string;
	placement?: "top" | "bottom" | "left" | "right";
}

export const HelpBubble: React.FC<HelpBubbleProps> = ({ helpText, placement = "right" }) => {
	const [isVisible, setIsVisible] = useState(false);

	return (
		<span
			className="help-bubble-container"
			onMouseEnter={() => setIsVisible(true)}
			onMouseLeave={() => setIsVisible(false)}
			style={{ position: "relative", display: "inline-block", marginLeft: "8px" }}
		>
			<i
				className="bi bi-question-circle"
				style={{
					fontSize: "14px",
					cursor: "default",
					opacity: 0.8,
				}}
				role="button"
				tabIndex={0}
				aria-label={`Help: ${helpText}`}
			/>
			{isVisible && (
				<div className={`help-tooltip help-tooltip-${placement}`}>
					{helpText}
					<div className={`help-tooltip-arrow help-tooltip-arrow-${placement}`}></div>
				</div>
			)}
		</span>
	);
};
