import React, { JSX, ReactNode, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import "./Popover.scss";

interface PopoverProps {
	/** Element the user clicks to toggle the popover. */
	trigger: ReactNode;
	/** Popover body. May be a render function receiving a `close` callback. */
	children: ReactNode | ((close: () => void) => ReactNode);
	className?: string;
	triggerClassName?: string;
	ariaLabel?: string;
}

/** Gap in px between the trigger and the popover. */
const GAP = 8;

/**
 * Click-triggered popover that renders its content in a portal (so it is not
 * clipped by overflow) below and right-aligned to the trigger. It animates in
 * and out, and closes on an outside click, on Escape, and when the page is
 * scrolled or resized.
 */
export const Popover = ({
	trigger,
	children,
	className = "",
	triggerClassName = "",
	ariaLabel,
}: PopoverProps): JSX.Element => {
	const triggerRef = useRef<HTMLSpanElement>(null);
	const popoverRef = useRef<HTMLDivElement>(null);
	const [coords, setCoords] = useState<{ top: number; left: number } | null>(null);
	const [shown, setShown] = useState<boolean>(false);
	const mounted: boolean = coords !== null;

	const openPopover = (): void => {
		if (!triggerRef.current) return;
		const rect: DOMRect = triggerRef.current.getBoundingClientRect();
		setCoords({ top: rect.bottom + GAP, left: rect.right });
	};

	const closePopover = (): void => setShown(false);

	const toggle = (event: React.MouseEvent): void => {
		event.stopPropagation();
		if (mounted && shown) closePopover();
		else openPopover();
	};

	const handleKeyDown = (event: React.KeyboardEvent): void => {
		if (event.key === "Enter" || event.key === " ") {
			event.preventDefault();
			event.stopPropagation();
			if (mounted && shown) closePopover();
			else openPopover();
		}
	};

	// Once mounted, flip to the open state on the next frame so the entry transition runs.
	useEffect(() => {
		if (!coords) return;
		const id = requestAnimationFrame(() => setShown(true));
		return (): void => cancelAnimationFrame(id);
	}, [coords]);

	// Unmount only after the exit transition has finished.
	const handleTransitionEnd = (): void => {
		if (!shown) setCoords(null);
	};

	// Fallback unmount in case the transition never fires (e.g. reduced motion).
	useEffect(() => {
		if (!mounted || shown) return;
		const id = window.setTimeout(() => setCoords(null), 250);
		return (): void => window.clearTimeout(id);
	}, [mounted, shown]);

	useEffect(() => {
		if (!mounted) return;
		const handlePointerDown = (event: MouseEvent): void => {
			const target = event.target as Node;
			if (popoverRef.current?.contains(target) || triggerRef.current?.contains(target)) return;
			// Ignore clicks inside portaled overlays opened from within the popover
			// (e.g. a select menu rendered into #jam-select-portal), which live
			// outside the popover DOM but are logically part of it.
			if (target instanceof Element && target.closest("#jam-select-portal")) return;
			closePopover();
		};
		const handleKey = (event: KeyboardEvent): void => {
			if (event.key === "Escape") closePopover();
		};
		document.addEventListener("mousedown", handlePointerDown);
		document.addEventListener("keydown", handleKey);
		window.addEventListener("scroll", closePopover, true);
		window.addEventListener("resize", closePopover);
		return (): void => {
			document.removeEventListener("mousedown", handlePointerDown);
			document.removeEventListener("keydown", handleKey);
			window.removeEventListener("scroll", closePopover, true);
			window.removeEventListener("resize", closePopover);
		};
	}, [mounted]);

	return (
		<span
			ref={triggerRef}
			className={`jam-popover-trigger ${triggerClassName}`.trim()}
			onClick={toggle}
			onKeyDown={handleKeyDown}
			role="button"
			tabIndex={0}
			aria-label={ariaLabel}
		>
			{trigger}
			{mounted &&
				coords &&
				createPortal(
					<div
						ref={popoverRef}
						className={`jam-popover ${shown ? "is-open" : ""} ${className}`.trim()}
						style={{ top: coords.top, left: coords.left }}
						onClick={(event): void => event.stopPropagation()}
						onTransitionEnd={handleTransitionEnd}
						role="dialog"
					>
						{typeof children === "function" ? children(closePopover) : children}
					</div>,
					document.body
				)}
		</span>
	);
};
