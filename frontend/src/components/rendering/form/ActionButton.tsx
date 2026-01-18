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

interface ActionButtonProps {
	id?: string;
	variant?: ButtonVariant;
	type?: "button" | "submit" | "reset";
	size?: "sm" | "lg";
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
	size = "lg",
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
	customLoadingContent,
	tooltip,
	tooltipPlacement = "top",
	style,
	...otherProps
}: ActionButtonProps): JSX.Element => {
	const buttonClasses = `${className} ${fullWidth ? "w-100" : ""}`.trim();

	const renderContent = (): React.ReactNode => {
		if (loading) {
			// Use custom loading content if provided
			if (customLoadingContent) {
				return customLoadingContent;
			}

			// Default loading content
			return (
				<>
					<div className="d-flex align-items-center justify-content-center">
						{loadingIcon ? (
							<i className={`${loadingIcon} me-2`}></i>
						) : (
							<Spinner
								as="span"
								animation="border"
								size="sm"
								role="status"
								aria-hidden="true"
								className="me-2"
							/>
						)}
						{loadingText}
					</div>
				</>
			);
		}

		// Use custom content if provided
		if (customContent) {
			return customContent;
		}

		// Default content
		return (
			<>
				<div className="d-flex align-items-center justify-content-center">
					{defaultIcon && <i className={`${defaultIcon} me-2`} style={{ fontSize: "20px" }}></i>}
					{defaultText}
				</div>
			</>
		);
	};

	const button = (
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
				size={size}
				disabled={disabled || loading}
				className={buttonClasses}
				onClick={onClick}
				style={{ ...style, height: "100%", width: "100%" }}
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
