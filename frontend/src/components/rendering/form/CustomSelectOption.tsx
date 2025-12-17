import React, { JSX, useRef } from "react";
import { components, OptionProps } from "react-select";

import { SelectOption } from "./FormOptions";

interface CustomOptionProps extends OptionProps<SelectOption, boolean> {
	onHover?: (option: SelectOption, position: { top: number; left: number }) => void;
	onHoverEnd?: () => void;
}

export const CustomSelectOption = (props: CustomOptionProps): JSX.Element => {
	const { onHover, onHoverEnd, data, innerProps } = props;
	const optionRef = useRef<HTMLDivElement>(null);
	const isClickingRef = useRef(false); // Use ref instead of state for immediate update

	const handleMouseEnter = (e: React.MouseEvent) => {
		if (innerProps?.onMouseEnter) {
			// @ts-ignore
			innerProps.onMouseEnter(e);
		}

		// Don't show preview if we're in the middle of a click
		if (isClickingRef.current) {
			console.log(`[Option ${data.label}] BLOCKED - currently clicking`);
			return;
		}

		if (optionRef.current && onHover) {
			const rect = optionRef.current.getBoundingClientRect();
			const position = {
				top: rect.top,
				left: rect.right + 10,
			};
			console.log(`[Option ${data.label}] Showing preview`);
			onHover(data, position);
		}
	};

	const handleMouseLeave = (e: React.MouseEvent) => {
		console.log(`[Option ${data.label}] mouseLeave`);

		if (innerProps?.onMouseLeave) {
			// @ts-ignore
			innerProps.onMouseLeave(e);
		}

		if (onHoverEnd) {
			onHoverEnd();
		}
	};

	const handleMouseDown = (e: React.MouseEvent) => {
		console.log(`[Option ${data.label}] === MOUSE DOWN - BLOCKING FUTURE HOVERS ===`);

		// Set ref immediately (synchronous, no re-render)
		isClickingRef.current = true;

		// Hide the preview immediately
		if (onHoverEnd) {
			onHoverEnd();
		}

		if (innerProps?.onMouseDown) {
			console.log(`[Option ${data.label}] Calling original onMouseDown`);
			// @ts-ignore
			innerProps.onMouseDown(e);
		}
	};

	const handleMouseUp = (e: React.MouseEvent) => {
		console.log(`[Option ${data.label}] === MOUSE UP - ALLOWING HOVERS AGAIN ===`);

		// Reset after a small delay to ensure click completes
		setTimeout(() => {
			isClickingRef.current = false;
			console.log(`[Option ${data.label}] Hover enabled again`);
		}, 100);

		if (innerProps?.onMouseUp) {
			// @ts-ignore
			innerProps.onMouseUp(e);
		}
	};

	const customInnerProps = {
		...innerProps,
		onMouseEnter: handleMouseEnter,
		onMouseLeave: handleMouseLeave,
		onMouseDown: handleMouseDown,
		onMouseUp: handleMouseUp,
		ref: optionRef,
	};

	return <components.Option {...props} innerProps={customInnerProps} />;
};
