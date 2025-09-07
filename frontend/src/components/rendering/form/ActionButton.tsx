import React, { JSX } from "react";
import { Button, Spinner } from "react-bootstrap";

interface ActionButtonProps {
	id?: string;
	variant?:
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
				{defaultIcon && <i className={`${defaultIcon} me-2`}></i>}
				{defaultText}
			</>
		);
	};

	return (
		<Button
			id={id}
			variant={variant}
			type={type}
			size={size}
			disabled={disabled || loading}
			className={buttonClasses}
			onClick={onClick}
			{...otherProps}
		>
			{renderContent()}
		</Button>
	);
};
