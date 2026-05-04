import React, { JSX, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Button, Spinner } from "react-bootstrap";
import "./ActionButton.scss";
import { useDelayedLoading } from "../../../hooks/useDelayedLoading";

export type ButtonVariant =
	| "primary"
	| "secondary"
	| "success"
	| "danger"
	| "warning"
	| "info"
	| "light"
	| "dark"
	| "outline-primary"
	| "outline-secondary"
	| "outline-success"
	| "outline-danger"
	| "outline-warning"
	| "outline-info"
	| "outline-light"
	| "outline-dark";

type ButtonSize = "sm" | "md" | "lg";

const BUTTON_HEIGHTS: Record<ButtonSize, number> = {
	sm: 36,
	md: 47,
	lg: 54,
};

interface ActionButtonProps {
	id?: string;
	variant?: ButtonVariant;
	type?: "button" | "submit" | "reset";
	size?: ButtonSize;
	className?: string;
	disabled?: boolean;
	loading?: boolean;
	loadingText?: string;
	defaultText?: string;
	loadingIcon?: string;
	defaultIcon?: string;
	fullWidth?: boolean;
	onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
	customContent?: React.ReactNode;
	customLoadingContent?: React.ReactNode;
	tooltip?: string;
	tooltipPlacement?: "top" | "bottom" | "left" | "right";
	style?: React.CSSProperties;
}

export const ActionButton = ({
	id,
	variant = "primary",
	type = "button",
	size = "md",
	className = "",
	disabled = false,
	loading = false,
	loadingText,
	defaultText,
	loadingIcon,
	defaultIcon,
	fullWidth = true,
	onClick,
	customContent,
	tooltip,
	tooltipPlacement = "top",
	style,
	...otherProps
}: ActionButtonProps): JSX.Element => {
	const visibleLoading: boolean = useDelayedLoading(loading);
	const wrapperRef = useRef<HTMLDivElement>(null);
	const [tooltipCoords, setTooltipCoords] = useState<{ top: number; left: number } | null>(null);

	const handleMouseEnter = () => {
		if (!tooltip || !wrapperRef.current) return;
		const rect = wrapperRef.current.getBoundingClientRect();
		const GAP = 8;
		let top: number, left: number;
		switch (tooltipPlacement) {
			case "top":
				top = rect.top - GAP;
				left = rect.left + rect.width / 2;
				break;
			case "bottom":
				top = rect.bottom + GAP;
				left = rect.left + rect.width / 2;
				break;
			case "left":
				top = rect.top + rect.height / 2;
				left = rect.left - GAP;
				break;
			case "right":
				top = rect.top + rect.height / 2;
				left = rect.right + GAP;
				break;
			default:
				top = rect.top - GAP;
				left = rect.left + rect.width / 2;
		}
		setTooltipCoords({ top, left });
	};

	const handleMouseLeave = () => setTooltipCoords(null);

	const buttonClasses = `${className} ${fullWidth ? "w-100" : ""}`.trim();
	const renderContent = (): React.ReactNode => {
		return (
			<div className="position-relative d-flex align-items-center justify-content-center w-100">
				{/* Default text + icon */}
				<span
					className={
						visibleLoading
							? "invisible d-flex align-items-center justify-content-center"
							: "d-flex align-items-center justify-content-center"
					}
					style={{ width: "100%", gap: "0.5rem" }} // reserve space for spinner/icon
				>
					{defaultIcon && <i className={`${defaultIcon}`} style={{ fontSize: "18px" }} />}
					{defaultText}
				</span>

				{/* Loading overlay */}
				{visibleLoading && (
					<span
						className="position-absolute d-flex align-items-center justify-content-center"
						style={{ inset: 0, gap: "0.5rem" }}
					>
						{loadingIcon ? (
							<i className={`${loadingIcon}`} />
						) : (
							<Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
						)}
						{loadingText ?? defaultText ?? "Loading..."}
					</span>
				)}
			</div>
		);
	};

	const buttonHeight: number = BUTTON_HEIGHTS[size];

	const button: JSX.Element = (
		<div
			tabIndex={-1}
			style={{
				cursor: "not-allowed",
				flex: "1 1",
				width: fullWidth ? "100%" : "auto",
			}}
		>
			<Button
				id={id}
				variant={variant}
				type={type}
				disabled={disabled || loading}
				className={buttonClasses}
				onClick={onClick}
				style={{
					...style,
					height: `${buttonHeight}px`,
					minHeight: `${buttonHeight}px`,
					display: "flex",
					alignItems: "center",
					justifyContent: "center",
					width: "100%",
				}}
				{...otherProps}
			>
				{renderContent()}
			</Button>
		</div>
	);

	// Wrap with tooltip if provided
	if (tooltip) {
		return (
			<>
				<div
					ref={wrapperRef}
					className="ab-tooltip-wrap"
					style={{ flex: "1 1", width: fullWidth ? "100%" : "auto" }}
					onMouseEnter={handleMouseEnter}
					onMouseLeave={handleMouseLeave}
				>
					{button}
				</div>
				{tooltipCoords &&
					createPortal(
						<div
							className={`ab-tooltip-portal ab-tooltip-portal--${tooltipPlacement}`}
							style={{ top: tooltipCoords.top, left: tooltipCoords.left }}
						>
							{tooltip}
						</div>,
						document.body
					)}
			</>
		);
	}

	return button;
};
