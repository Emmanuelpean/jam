import React from "react";
import { Tooltip, TooltipPlacement } from "../Tooltip/Tooltip";

interface HelpBubbleProps {
	helpText: string;
	placement?: TooltipPlacement;
	size?: string;
}

export const HelpBubble: React.FC<HelpBubbleProps> = ({
	helpText,
	placement = "right",
	size = "12px",
}: HelpBubbleProps): JSX.Element => {
	return (
		<Tooltip content={helpText} placement={placement}>
			<i
				className="bi bi-question-circle"
				style={{
					fontSize: size,
					cursor: "default",
					opacity: 0.8,
					marginLeft: "7px",
				}}
				role="button"
				tabIndex={0}
				aria-label={`Help: ${helpText}`}
			/>
		</Tooltip>
	);
};
