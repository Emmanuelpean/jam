import React, { useState, JSX } from "react";
import "./Accordion.scss";

interface BaseAccordionProps {
	header: React.ReactNode;
	children: React.ReactNode;
	defaultOpen?: boolean;
	isOpen?: boolean;
	onToggle?: () => void;
	className?: string;
}

export const Accordion = ({
	header,
	children,
	defaultOpen = false,
	isOpen: controlledIsOpen,
	onToggle,
	className,
}: BaseAccordionProps): JSX.Element => {
	const [internalIsOpen, setInternalIsOpen] = useState(defaultOpen);
	const isControlled: boolean = controlledIsOpen !== undefined;
	const isOpen: boolean = isControlled ? !!controlledIsOpen : internalIsOpen;

	const handleToggle = (): void => {
		if (onToggle) {
			onToggle();
		}
		if (!isControlled) {
			setInternalIsOpen((prev: boolean): boolean => !prev);
		}
	};

	return (
		<div className={`simple-accordion ${className || ""}`} style={{ paddingLeft: "9px", paddingRight: "9px" }}>
			<div
				className="simple-accordion-header d-flex align-items-center justify-content-between py-2"
				onClick={handleToggle}
				style={{ cursor: "pointer", userSelect: "none" }}
			>
				<div className="d-flex align-items-center">{header}</div>
				<i
					className={`bi bi-chevron-down text-muted accordion-chevron ${isOpen ? "accordion-chevron-open" : ""}`}
				></i>
			</div>
			<div
				style={{
					display: "grid",
					gridTemplateRows: isOpen ? "1fr" : "0fr",
					transition: "grid-template-rows 0.3s ease-in-out",
				}}
			>
				<div style={{ overflow: "hidden" }}>
					<div className="simple-accordion-content">{children}</div>
				</div>
			</div>
		</div>
	);
};
