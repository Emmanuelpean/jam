import React, { JSX, ReactNode, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import "./Popover.scss";

interface PopoverProps {
	trigger: ReactNode;
	children: ReactNode | ((close: () => void) => ReactNode);
	className?: string;
	triggerClassName?: string;
	ariaLabel?: string;
	onClose?: () => void;
}

const GAP = 8;

export const Popover = ({
	trigger,
	children,
	className = "",
	triggerClassName = "",
	ariaLabel,
	onClose,
}: PopoverProps): JSX.Element => {
	const triggerRef = useRef<HTMLSpanElement>(null);
	const popoverRef = useRef<HTMLDivElement>(null);
	const [coords, setCoords] = useState<{ top: number; left: number } | null>(null);
	const [shown, setShown] = useState<boolean>(false);
	const mounted: boolean = coords !== null;

	const shownRef = useRef<boolean>(false);
	useEffect(() => {
		shownRef.current = shown;
	}, [shown]);

	const openPopover = (): void => {
		if (!triggerRef.current) return;
		const rect: DOMRect = triggerRef.current.getBoundingClientRect();
		setCoords({ top: rect.bottom + GAP, left: rect.right });
	};

	const closePopover = (): void => {
		if (shownRef.current) onClose?.();
		setShown(false);
	};

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

	useEffect(() => {
		if (!coords) return;
		const id = requestAnimationFrame(() => setShown(true));
		return (): void => cancelAnimationFrame(id);
	}, [coords]);

	const handleTransitionEnd = (): void => {
		if (!shown) setCoords(null);
	};

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
					<>
						<div
							className={`jam-popover-backdrop ${shown ? "is-open" : ""}`.trim()}
							onClick={(event): void => {
								event.stopPropagation();
								closePopover();
							}}
						/>
						<div
							ref={popoverRef}
							className={`jam-popover ${shown ? "is-open" : ""} ${className}`.trim()}
							style={{ top: coords.top, left: coords.left }}
							onClick={(event): void => event.stopPropagation()}
							onTransitionEnd={handleTransitionEnd}
							role="dialog"
						>
							{typeof children === "function" ? children(closePopover) : children}
						</div>
					</>,
					document.body
				)}
		</span>
	);
};
