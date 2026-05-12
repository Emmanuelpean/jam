import React, { JSX, useEffect, useRef, useState } from "react";
import "./TourHintPopup.scss";

interface Props {
	onClose: () => void;
}

export function TourHintPopup({ onClose }: Props): JSX.Element | null {
	const [position, setPosition] = useState<{ top: number; left: number } | null>(null);
	const rafRef = useRef<number | null>(null);

	useEffect(() => {
		const track = (): void => {
			const el = document.getElementById("take-a-tour-btn");
			if (el) {
				const rect = el.getBoundingClientRect();
				const top = rect.top + rect.height / 2;
				const left = rect.right + 10;
				setPosition((prev) => (prev && prev.top === top && prev.left === left ? prev : { top, left }));
			}
			rafRef.current = requestAnimationFrame(track);
		};
		rafRef.current = requestAnimationFrame(track);
		return (): void => {
			if (rafRef.current) cancelAnimationFrame(rafRef.current);
		};
	}, []);

	if (!position) return null;

	return (
		<div className="tour-hint-popup" style={{ top: position.top, left: position.left }}>
			<div className="tour-hint-arrow" />
			<div className="tour-hint-bubble">
				<p>
					Take a tour anytime from the <strong>Take a Tour</strong> panel.
				</p>
				<button className="tour-hint-close" onClick={onClose} aria-label="Dismiss">
					<i className="bi bi-x" />
				</button>
			</div>
		</div>
	);
}
