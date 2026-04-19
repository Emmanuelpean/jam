import React, { JSX, useEffect, useLayoutEffect, useRef, useState } from "react";
import { useTour } from "../../contexts/TourContext";
import { TOURS } from "../GuidedTour/tourSteps";
import "./TourSelectPanel.scss";

export function TourSelectPanel(): JSX.Element | null {
	const { isTourSelectOpen, closeTourSelect, startTour, completedTourIds, isTourActive } = useTour();
	const [anchorRect, setAnchorRect] = useState<DOMRect | null>(null);
	const [panelTop, setPanelTop] = useState<number>(0);
	const panelRef = useRef<HTMLDivElement>(null);
	const closeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

	useLayoutEffect(() => {
		if (!anchorRect || !panelRef.current) return;
		const panelHeight = panelRef.current.offsetHeight;
		const margin = 6;
		const clamped = Math.min(anchorRect.top, window.innerHeight - panelHeight - margin);
		setPanelTop(Math.max(clamped, margin));
	}, [anchorRect]);

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
			ref={panelRef}
			id="tsp-panel"
			className="tsp-panel"
			style={{ top: panelTop || anchorRect.top, left: anchorRect.right + 12 }}
			role="dialog"
			aria-label="Guided Tours"
		>
			<div className="tsp-header">
				<p className="tsp-heading">Guided Tours</p>
				<span id="tsp-progress" className="tsp-progress">
					{TOURS.filter((t) => completedTourIds.has(t.id)).length} / {TOURS.length}
				</span>
			</div>
			<ul className="tsp-list">
				{TOURS.map((tour) => {
					const completed = completedTourIds.has(tour.id);
					return (
						<li key={tour.id}>
							<button id={`tsp-item-${tour.id}`} className="tsp-item" disabled={isTourActive} onClick={() => void startTour(tour.id)}>
								<i id={`tsp-icon-${tour.id}`} className={`bi bi-check-circle ${completed ? "tsp-icon--done" : "tsp-icon"}`} />
								<span>{tour.title}</span>
							</button>
						</li>
					);
				})}
			</ul>
		</div>
	);
}
