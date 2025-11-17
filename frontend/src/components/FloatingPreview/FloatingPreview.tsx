import React, { JSX, useEffect, useRef, useState } from "react";
import { Card } from "react-bootstrap";
import { ModalViewField, ModalViewFields, renderModalViewField } from "../rendering/view/ModalFields";
import "./FloatingPreview.css";

export interface FloatingPreviewProps {
	data: any;
	fields: ModalViewFields;
	position: { top: number; left: number };
	show: boolean;
}

export const FloatingPreview = ({ data, fields, position, show }: FloatingPreviewProps): JSX.Element | null => {
	const [adjustedPosition, setAdjustedPosition] = useState(position);
	const [arrowOffset, setArrowOffset] = useState(0);
	const previewRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (!show || !previewRef.current) return;

		const previewRect: DOMRect = previewRef.current.getBoundingClientRect();
		const viewportHeight: number = window.innerHeight;
		const viewportWidth: number = window.innerWidth;

		let newTop = position.top;
		let newLeft = position.left;
		let newArrowOffset = 0;

		// Check if preview would overflow bottom of viewport
		if (position.top + previewRect.height > viewportHeight - 20) {
			newTop = Math.max(20, viewportHeight - previewRect.height - 20);
			newArrowOffset = position.top - newTop;
		}

		// Check if preview would overflow top of viewport
		if (newTop < 20) {
			newTop = 20;
			newArrowOffset = position.top - 20;
		}

		// Check if preview would overflow right edge
		if (newLeft + previewRect.width > viewportWidth - 20) {
			newLeft = viewportWidth - previewRect.width - 20;
		}

		// Clamp arrow offset to stay within preview bounds
		const maxOffset: number = previewRect.height - 40;
		const minOffset = 20;
		newArrowOffset = Math.max(minOffset, Math.min(maxOffset, newArrowOffset));

		setAdjustedPosition({ top: newTop, left: newLeft });
		setArrowOffset(newArrowOffset);
	}, [show, position]);

	// Prevent clicks from propagating to prevent closing the select
	const handleMouseDown = (e: React.MouseEvent): void => {
		e.preventDefault();
		e.stopPropagation();
	};

	if (!show || !data) return null;

	const renderFieldGroup = (item: ModalViewField | ModalViewField[], index: number): JSX.Element => {
		const itemList: ModalViewField[] = Array.isArray(item) ? item : [item];

		return (
			<div key={`preview-group-${index}`} className="row mb-3">
				{itemList.map((field: ModalViewField): JSX.Element => {
					return (
						<div key={field.key} className="col-12">
							{renderModalViewField(field as ModalViewField, data, `floating-preview-${data.id}`)}
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
			<div
				className="floating-preview-arrow"
				style={{
					top: arrowOffset > 0 ? `${arrowOffset}px` : "20px",
				}}
			/>

			<Card>
				<Card.Body>{fields.map((item, index: number) => renderFieldGroup(item, index))}</Card.Body>
			</Card>
		</div>
	);
};
