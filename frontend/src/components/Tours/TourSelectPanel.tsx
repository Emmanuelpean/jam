import React, { JSX, useEffect, useLayoutEffect, useRef, useState } from "react";
import { useTour } from "../../contexts/TourContext";
import { useAuth } from "../../contexts/AuthContext";
import { isTourGroup, TOUR_STRUCTURE, TOURS, TourDefinition } from "../GuidedTour/tourSteps";
import "./TourSelectPanel.scss";

export function TourSelectPanel(): JSX.Element | null {
	const { isTourSelectOpen, closeTourSelect, startTour, completedTourIds, isTourActive } = useTour();
	const { currentUser } = useAuth();
	const isPremium = currentUser?.premium.is_active ?? false;
	const [anchorRect, setAnchorRect] = useState<DOMRect | null>(null);
	const [panelTop, setPanelTop] = useState<number>(0);
	const panelRef = useRef<HTMLDivElement>(null);
	const closeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

	useLayoutEffect(() => {
		if (!anchorRect || !panelRef.current) return;
		const panelHeight = panelRef.current.offsetHeight;
		const margin = 6;
		const ideal = anchorRect.bottom - panelHeight;
		setPanelTop(Math.max(ideal, margin));
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

	const visibleStructure = TOUR_STRUCTURE.filter((item) => !isTourGroup(item) || isPremium || item.id !== "premium");
	const visibleTours = TOURS.filter((t) => isPremium || !["import-scraped-job", "scraping-filters"].includes(t.id));
	const implementedTours = visibleTours.filter((t) => !t.comingSoon);
	const completedCount = implementedTours.filter((t) => completedTourIds.has(t.id)).length;

	const renderTourItem = (tour: TourDefinition, indented: boolean): JSX.Element => {
		const completed = completedTourIds.has(tour.id);
		return (
			<li key={tour.id}>
				<button
					id={`tsp-item-${tour.id}`}
					className={`tsp-item${indented ? " tsp-item--indented" : ""}`}
					disabled={isTourActive || !!tour.comingSoon}
					onClick={tour.comingSoon ? undefined : (): void => void startTour(tour.id)}
				>
					<i
						id={`tsp-icon-${tour.id}`}
						className={`bi bi-check-circle ${completed ? "tsp-icon--done" : "tsp-icon"}`}
					/>
					<span className="tsp-item-title">{tour.title}</span>
					{tour.comingSoon && <span className="tsp-badge tsp-badge--soon">Soon</span>}
				</button>
			</li>
		);
	};

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
					{completedCount} / {implementedTours.length}
				</span>
			</div>
			<ul className="tsp-list">
				{visibleStructure.map((item) => {
					if (isTourGroup(item)) {
						return (
							<li key={item.id} className="tsp-group">
								<div className="tsp-group-header">
									<i className={`bi bi-${item.icon} tsp-group-icon`} />
									<span className="tsp-group-title">{item.title}</span>
									{item.badge && <span className="tsp-badge tsp-badge--section">{item.badge}</span>}
								</div>
								<ul className="tsp-sublist">
									{item.tours.map((tour) => renderTourItem(tour, true))}
								</ul>
							</li>
						);
					}
					return renderTourItem(item, false);
				})}
			</ul>
		</div>
	);
}
