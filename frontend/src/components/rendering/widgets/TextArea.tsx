import React, { JSX, useEffect, useRef } from "react";
import { Form } from "react-bootstrap";
import { WidgetProps } from "./WidgetRenders";
import "./TextArea.scss";
import { toKey } from "../../../utils/StringUtils";

export const Textarea = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	const textareaRef = useRef<HTMLTextAreaElement | null>(null);
	const overlayRef = useRef<HTMLDivElement | null>(null);
	const charCount = field.maxChars ? (value || "").length : 0;
	const isOverLimit = field.maxChars ? charCount > field.maxChars : false;

	useEffect((): void => {
		if (field.autoHeight) {
			const el: HTMLTextAreaElement | null = textareaRef.current;
			if (!el) return;
			el.style.height = "auto";
			el.style.height = `${el.scrollHeight + 7}px`;
		}
	}, [value]);

	const syncScroll = (): void => {
		if (overlayRef.current && textareaRef.current) {
			overlayRef.current.scrollTop = textareaRef.current.scrollTop;
		}
	};

	return (
		<>
			<div className="textarea-overflow-wrapper">
				{isOverLimit && field.maxChars && (
					<div ref={overlayRef} className="textarea-highlight-overlay" aria-hidden="true">
						<span>{(value || "").slice(0, field.maxChars)}</span>
						<mark className="textarea-overflow-mark">{(value || "").slice(field.maxChars)}</mark>
					</div>
				)}
				<Form.Control
					as="textarea"
					ref={textareaRef}
					id={toKey(field.key)}
					rows={field.rows || 3}
					name={toKey(field.key)}
					value={value || ""}
					onChange={handleChange}
					onScroll={syncScroll}
					placeholder={field.placeholder}
					isInvalid={!!error || isOverLimit}
					className={`optimized-textarea${isOverLimit ? " overflow-active" : ""}`}
					disabled={field.isDisabled}
				/>
			</div>
		</>
	);
};
