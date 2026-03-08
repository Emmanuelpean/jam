import React, { useRef, useState } from "react";
import "./HelpBubble.scss";

interface HelpBubbleProps {
	helpText: string;
	placement?: "top" | "bottom" | "left" | "right";
	size?: string;
}

export const HelpBubble: React.FC<HelpBubbleProps> = ({ helpText, placement = "right", size = "12.6px" }) => {
	const [position, setPosition] = useState<{ top: number; left: number } | null>(null);
	const iconRef = useRef<HTMLSpanElement>(null);

	const showTooltip = () => {
		if (!iconRef.current) return;
		const rect = iconRef.current.getBoundingClientRect();
		switch (placement) {
			case "top":
				setPosition({ top: rect.top - 8, left: rect.left + rect.width / 2 });
				break;
			case "bottom":
				setPosition({ top: rect.bottom + 8, left: rect.left + rect.width / 2 });
				break;
			case "left":
				setPosition({ top: rect.top + rect.height / 2, left: rect.left - 8 });
				break;
			default:
				setPosition({ top: rect.top + rect.height / 2, left: rect.right + 8 });
		}
	};

	return (
		<span
			className="help-bubble-container"
			ref={iconRef}
			onMouseEnter={showTooltip}
			onMouseLeave={() => setPosition(null)}
			style={{ position: "relative", display: "inline-block", marginLeft: "7.2px" }}
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
			{position && (
				<div
					className={`help-tooltip help-tooltip-${placement}`}
					style={{
						position: "fixed",
						top: position.top,
						left: position.left,
					}}
				>
					{helpText}
					<div className={`help-tooltip-arrow help-tooltip-arrow-${placement}`}></div>
				</div>
			)}
		</span>
	);
};
