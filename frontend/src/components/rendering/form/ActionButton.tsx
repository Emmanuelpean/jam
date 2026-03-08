import React, { JSX } from "react";
import { Button, OverlayTrigger, Spinner, Tooltip } from "react-bootstrap";

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
	sm: 40,
	md: 52,
	lg: 60,
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
	const buttonClasses = `${className} ${fullWidth ? "w-100" : ""}`.trim();
	const renderContent = (): React.ReactNode => {
		return (
			<div className="position-relative d-flex align-items-center justify-content-center w-100">
				{/* Default text + icon */}
				<span
					className={
						loading
							? "invisible d-flex align-items-center justify-content-center"
							: "d-flex align-items-center justify-content-center"
					}
					style={{ width: "100%", gap: "0.5rem" }} // reserve space for spinner/icon
				>
					{defaultIcon && <i className={`${defaultIcon}`} style={{ fontSize: "18px" }} />}
					{defaultText}
				</span>

				{/* Loading overlay */}
				{loading && (
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
			tabIndex={0}
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
			<OverlayTrigger placement={tooltipPlacement} overlay={<Tooltip id={`${id}-tooltip`}>{tooltip}</Tooltip>}>
				{button}
			</OverlayTrigger>
		);
	}

	return button;
};
