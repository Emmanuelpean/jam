import React, { JSX, useEffect, useRef, useState } from "react";
import { useTour } from "../../contexts/TourContext";
import { TOURS } from "../GuidedTour/tourSteps";
import "./TourSelectPanel.scss";

export function TourSelectPanel(): JSX.Element | null {
	const { isTourSelectOpen, closeTourSelect, startTour, completedTourIds, isTourActive } = useTour();
	const [anchorRect, setAnchorRect] = useState<DOMRect | null>(null);
	const closeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

	useEffect(() => {
		if (!isTourSelectOpen) {
			setAnchorRect(null);
			return;
		}
		const btn = document.getElementById("take-a-tour-btn");
		if (btn) setAnchorRect(btn.getBoundingClientRect());
	}, [isTourSelectOpen]);

	// Close when mouse leaves both the panel and the sidebar
	useEffect(() => {
		if (!isTourSelectOpen || !anchorRect) return;

		const scheduleClose = (): void => {
			if (closeTimerRef.current) clearTimeout(closeTimerRef.current);
			closeTimerRef.current = setTimeout(() => {
				const panel = document.getElementById("tsp-panel");
				const sidebar = document.querySelector(".custom-sidebar");
				if (!panel?.matches(":hover") && !sidebar?.matches(":hover")) closeTourSelect();
			}, 200);
		};

		const cancelClose = (): void => {
			if (closeTimerRef.current) {
				clearTimeout(closeTimerRef.current);
				closeTimerRef.current = null;
			}
		};

		const panel = document.getElementById("tsp-panel");
		const sidebar = document.querySelector<HTMLElement>(".custom-sidebar");

		panel?.addEventListener("mouseleave", scheduleClose);
		panel?.addEventListener("mouseenter", cancelClose);
		sidebar?.addEventListener("mouseleave", scheduleClose);
		sidebar?.addEventListener("mouseenter", cancelClose);

		return () => {
			cancelClose();
			panel?.removeEventListener("mouseleave", scheduleClose);
			panel?.removeEventListener("mouseenter", cancelClose);
			sidebar?.removeEventListener("mouseleave", scheduleClose);
			sidebar?.removeEventListener("mouseenter", cancelClose);
		};
	}, [isTourSelectOpen, anchorRect, closeTourSelect]);

	if (!isTourSelectOpen || !anchorRect) return null;

	return (
		<div
			id="tsp-panel"
			className="tsp-panel"
			style={{ top: anchorRect.top, left: anchorRect.right + 8 }}
			role="dialog"
			aria-label="Guided Tours"
		>
			<div className="tsp-header">
				<p className="tsp-heading">Guided Tours</p>
				<span className="tsp-progress">
					{TOURS.filter((t) => completedTourIds.has(t.id)).length} / {TOURS.length}
				</span>
			</div>
			<ul className="tsp-list">
				{TOURS.map((tour) => {
					const completed = completedTourIds.has(tour.id);
					return (
						<li key={tour.id}>
							<button className="tsp-item" disabled={isTourActive} onClick={() => startTour(tour.id)}>
								<i className={`bi bi-check-circle ${completed ? "tsp-icon--done" : "tsp-icon"}`} />
								<span>{tour.title}</span>
							</button>
						</li>
					);
				})}
			</ul>
		</div>
	);
}
