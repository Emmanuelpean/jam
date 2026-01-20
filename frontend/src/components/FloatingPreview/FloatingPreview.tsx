import React, { JSX, useEffect, useRef, useState } from "react";
import { Card } from "react-bootstrap";
import {
	ModalViewField,
	ModalViewFields,
	renderModalViewField,
} from "../rendering/view/ModalFields";
import "./FloatingPreview.scss";
import { getColumnClass, normaliseArray } from "../../utils/Utils";

export interface FloatingPreviewProps {
	data: any;
	fields: ModalViewFields;
	position: { top: number; left: number };
	show: boolean;
}

export const FloatingPreview = ({
	data,
	fields,
	position,
	show,
}: FloatingPreviewProps): JSX.Element | null => {
	const [adjustedPosition, setAdjustedPosition] = useState(position);
	const previewRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (!show || !previewRef.current) return;

		const previewRect: DOMRect = previewRef.current.getBoundingClientRect();
		const viewportHeight: number = window.innerHeight;
		const viewportWidth: number = window.innerWidth;

		let newTop = position.top;
		let newLeft = position.left;

		// Check if preview would overflow bottom of viewport
		if (position.top + previewRect.height > viewportHeight - 20) {
			newTop = Math.max(20, viewportHeight - previewRect.height - 20);
		}

		// Check if preview would overflow top of viewport
		if (newTop < 20) {
			newTop = 20;
		}

		// Check if preview would overflow right edge
		if (newLeft + previewRect.width > viewportWidth - 20) {
			newLeft = viewportWidth - previewRect.width - 20;
		}

		setAdjustedPosition({ top: newTop, left: newLeft });
	}, [show, position]);

	// Prevent clicks from propagating to prevent closing the select
	const handleMouseDown = (e: React.MouseEvent): void => {
		e.preventDefault();
		e.stopPropagation();
	};

	if (!show || !data) return null;

	const renderFieldGroup = (
		item: ModalViewField | ModalViewField[],
		index: number
	): JSX.Element => {
		const itemList: ModalViewField[] = normaliseArray(item);
		const columnClass = getColumnClass(itemList.length);

		return (
			<div key={`preview-group-${index}`} className="row">
				{itemList.map((field: ModalViewField): JSX.Element => {
					return (
						<div key={field.key} className={columnClass}>
							{renderModalViewField(
								field as ModalViewField,
								data,
								`floating-preview-${data.id}`
							)}
						</div>
					);
				})}
			</div>
		);
	};

	return (
		<div
			ref={previewRef}
			className="floating-preview-container"
			style={{
				position: "fixed",
				top: `${adjustedPosition.top}px`,
				left: `${adjustedPosition.left}px`,
				zIndex: 9999,
				maxWidth: "400px",
			}}
			onMouseDown={handleMouseDown}
		>
			<Card>
				<Card.Body>
					{fields.map((item, index: number) => renderFieldGroup(item, index))}
				</Card.Body>
			</Card>
		</div>
	);
};
