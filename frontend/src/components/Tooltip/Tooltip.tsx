import React, { JSX, ReactNode, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import "./Tooltip.scss";

export type TooltipPlacement = "top" | "bottom" | "left" | "right";

export const TITLE_TOOLTIP_DELAY = 1000;

interface TooltipProps {
	content: ReactNode;
	placement?: TooltipPlacement;
	children: ReactNode;
	disabled?: boolean;
	delay?: number;
	className?: string;
	style?: React.CSSProperties;
	maxWidth?: number | string;
}

/** Gap in px between the target and the tooltip bubble (and thus the arrow tip). */
const GAP = 10;

export const Tooltip = ({
	content,
	placement = "top",
	children,
	disabled = false,
	delay = 0,
	className = "",
	style,
	maxWidth,
}: TooltipProps): JSX.Element => {
	const wrapperRef = useRef<HTMLSpanElement>(null);
	const timerRef = useRef<number | null>(null);
	const [coords, setCoords] = useState<{ top: number; left: number } | null>(null);

	const clearTimer = (): void => {
		if (timerRef.current !== null) {
			window.clearTimeout(timerRef.current);
			timerRef.current = null;
		}
	};

	const position = (): void => {
		if (!wrapperRef.current) return;
		const target = wrapperRef.current.firstElementChild ?? wrapperRef.current;
		const rect = target.getBoundingClientRect();
		switch (placement) {
			case "bottom":
				setCoords({ top: rect.bottom + GAP, left: rect.left + rect.width / 2 });
				break;
			case "left":
				setCoords({ top: rect.top + rect.height / 2, left: rect.left - GAP });
				break;
			case "right":
				setCoords({ top: rect.top + rect.height / 2, left: rect.right + GAP });
				break;
			default:
				setCoords({ top: rect.top - GAP, left: rect.left + rect.width / 2 });
		}
	};

	const show = (): void => {
		if (disabled || !content) return;
		clearTimer();
		if (delay > 0) {
			timerRef.current = window.setTimeout(position, delay);
		} else {
			position();
		}
	};

	const hide = (): void => {
		clearTimer();
		setCoords(null);
	};

	// Cancel a pending show if the tooltip unmounts mid-delay.
	useEffect(() => clearTimer, []);

	return (
		<span
			ref={wrapperRef}
			className={`jam-tooltip-wrap ${className}`.trim()}
			style={style}
			onMouseEnter={show}
			onMouseLeave={hide}
			onFocus={show}
			onBlur={hide}
		>
			{children}
			{coords &&
				createPortal(
					<div
						className={`jam-tooltip jam-tooltip--${placement}`}
						style={{ top: coords.top, left: coords.left, maxWidth }}
						role="tooltip"
					>
						{content}
					</div>,
					document.body
				)}
		</span>
	);
};
