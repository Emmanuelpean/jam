import React from "react";
import { HelpBubble } from "../widgets/HelpBubble";

interface GenericAccordionProps<T = any> {
	title: string;
	data: T[];
	itemId?: number;
	children: (data: T[], onChange?: () => void) => React.ReactNode;
	icon?: string;
	defaultOpen?: boolean;
	helpText?: string;
}

export const Accordion = <T,>({
	title,
	data,
	children,
	icon,
	defaultOpen = false,
	helpText,
}: GenericAccordionProps<T>) => {
	const [isOpen, setIsOpen] = React.useState(defaultOpen);

	return (
		<div className="simple-accordion" style={{ paddingLeft: "10px", paddingRight: "10px" }}>
			<div
				className="simple-accordion-header d-flex align-items-center justify-content-between py-2 border-bottom"
				onClick={() => setIsOpen(!isOpen)}
				style={{ cursor: "pointer" }}
			>
				<div className="d-flex align-items-center">
					{icon && <i className={`${icon} me-2`}></i>}
					<span className="fw-medium">{title}</span>
					<span className="text-muted ms-2">({data?.length || 0})</span>
					{helpText && <HelpBubble helpText={helpText} size="17px" />}
				</div>
				<i className={`bi ${isOpen ? "bi-chevron-up" : "bi-chevron-down"} text-muted`}></i>
			</div>
			{isOpen && <div className="simple-accordion-content">{children(data)}</div>}
		</div>
	);
};
