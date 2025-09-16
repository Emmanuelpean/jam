import React, { useState, useRef } from "react";
import ReactDOM from "react-dom";
import "./HelpBubble.css";
interface HelpBubbleProps {
	helpText: string;
	placement?: "top" | "bottom" | "left" | "right";
	size?: string;
	container?: HTMLElement; // Add this prop
}

export const HelpBubble: React.FC<HelpBubbleProps> = ({ helpText, placement = "right", size = "14px", container }) => {
	const [isVisible, setIsVisible] = useState(false);
	const iconRef = useRef<HTMLSpanElement>(null);

	const getTooltipPosition = () => {
		if (!iconRef.current) return { top: 0, left: 0 };
		const rect = iconRef.current.getBoundingClientRect();
		switch (placement) {
			case "top":
				return { top: rect.top - 8, left: rect.left + rect.width / 2 };
			case "bottom":
				return { top: rect.bottom + 8, left: rect.left + rect.width / 2 };
			case "left":
				return { top: rect.top + rect.height / 2, left: rect.left - 8 };
			default:
				return { top: rect.top + rect.height / 2, left: rect.right + 8 };
		}
	};

	const tooltip = isVisible
		? ReactDOM.createPortal(
				<div
					className={`help-tooltip help-tooltip-${placement}`}
					style={{
						position: "fixed",
						top: getTooltipPosition().top,
						left: getTooltipPosition().left,
						pointerEvents: "none",
						zIndex: 9999,
					}}
				>
					{helpText}
					<div className={`help-tooltip-arrow help-tooltip-arrow-${placement}`}></div>
				</div>,
				container || document.body, // Use container if provided
			)
		: null;

	return (
		<span
			className="help-bubble-container"
			ref={iconRef}
			onMouseEnter={() => setIsVisible(true)}
			onMouseLeave={() => setIsVisible(false)}
			style={{ position: "relative", display: "inline-block", marginLeft: "8px" }}
		>
			<i
				className="bi bi-question-circle"
				style={{
					fontSize: size,
					cursor: "default",
					opacity: 0.8,
				}}
				role="button"
				tabIndex={0}
				aria-label={`Help: ${helpText}`}
			/>
			{tooltip}
		</span>
	);
};
