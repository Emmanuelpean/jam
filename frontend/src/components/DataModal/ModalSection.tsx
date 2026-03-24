import React, { JSX, ReactNode } from "react";
import { Accordion } from "react-bootstrap";

export interface ModalSectionProps {
	sectionKey: string;
	title: ReactNode;
	icon?: string;
	expanded?: boolean;
	onToggle?: (sectionKey: string, isExpanded: boolean) => void;
	children: ReactNode;
}

export const ModalSection = ({
	sectionKey,
	title,
	icon,
	expanded = true,
	onToggle,
	children,
}: ModalSectionProps): JSX.Element => {
	const handleSelect = (eventKey: string | string[] | null | undefined): void => {
		const isExpanded: boolean = eventKey !== null && eventKey !== undefined && eventKey === sectionKey;
		onToggle?.(sectionKey, isExpanded);
	};

	return (
		<Accordion
			activeKey={expanded ? sectionKey : undefined}
			onSelect={handleSelect}
			style={{ paddingBottom: "1rem" }}
			id={sectionKey}
		>
			<Accordion.Item eventKey={sectionKey}>
				<Accordion.Header>
					{icon && <i className={`${icon} me-2`} />}
					<span>{title}</span>
				</Accordion.Header>
				<Accordion.Body>{children}</Accordion.Body>
			</Accordion.Item>
		</Accordion>
	);
};
