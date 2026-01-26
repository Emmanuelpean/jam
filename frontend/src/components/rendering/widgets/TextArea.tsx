import React, { JSX, useEffect, useRef } from "react";
import { Form } from "react-bootstrap";
import { WidgetProps } from "./WidgetRenders";
import "./TextArea.scss";
import { toKey } from "../../../utils/StringUtils";

export const Textarea = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
	const ref = useRef<HTMLTextAreaElement | null>(null);

	useEffect((): void => {
		if (field.autoHeight) {
			const el: HTMLTextAreaElement | null = ref.current;
			if (!el) return;
			el.style.height = "auto";
			el.style.height = `${el.scrollHeight + 7}px`;
		}
	}, [value]);

	return (
		<Form.Control
			as="textarea"
			ref={ref}
			id={toKey(field.name)}
			rows={field.rows || 3}
			name={toKey(field.name)}
			value={value || ""}
			onChange={handleChange}
			placeholder={field.placeholder}
			isInvalid={!!error}
			className="optimized-textarea"
			disabled={field.isDisabled}
		/>
	);
};
