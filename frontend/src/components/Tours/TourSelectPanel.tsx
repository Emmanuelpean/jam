import React, { JSX, useEffect, useLayoutEffect, useRef, useState } from "react";
import { useTour } from "../../contexts/TourContext";
import { useAuth } from "../../contexts/AuthContext";
import { TOURS, TourDefinition } from "../GuidedTour/tourSteps";
import "./TourSelectPanel.scss";

const CLOSE_ANIMATION_MS = 150;

export function TourSelectPanel(): JSX.Element | null {
	const { isTourSelectOpen, closeTourSelect, startTour, completedTourIds, isTourActive } = useTour();
	const { currentUser } = useAuth();
	const isPremium = currentUser?.premium.is_active ?? false;
	const [anchorRect, setAnchorRect] = useState<DOMRect | null>(null);
	const [panelTop, setPanelTop] = useState<number>(0);
	const [isClosing, setIsClosing] = useState<boolean>(false);
	const panelRef = useRef<HTMLDivElement>(null);
	const exitTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

	useLayoutEffect(() => {
		if (!anchorRect || !panelRef.current) return;
		const panelHeight = panelRef.current.offsetHeight;
		const margin = 6;
		const bottomGap = 12;
		const ideal = anchorRect.bottom - panelHeight - bottomGap;
		setPanelTop(Math.max(ideal, margin));
	}, [anchorRect]);

	useEffect(() => {
		if (!isTourSelectOpen) {
			if (anchorRect) {
				setIsClosing(true);
				exitTimerRef.current = setTimeout(() => {
					setIsClosing(false);
					setAnchorRect(null);
				}, CLOSE_ANIMATION_MS);
			}
			return () => {
				if (exitTimerRef.current) clearTimeout(exitTimerRef.current);
			};
		}
		setIsClosing(false);
		if (exitTimerRef.current) clearTimeout(exitTimerRef.current);

		const sidebar = document.querySelector(".custom-sidebar");
		if (!sidebar) return;

		const updateRect = (): void => setAnchorRect(sidebar.getBoundingClientRect());
		updateRect();

		const observer = new ResizeObserver(updateRect);
		observer.observe(sidebar);
		return () => observer.disconnect();
	}, [isTourSelectOpen]);

	const visibleTours = TOURS.filter((t) => isPremium || !t.premium);
	const implementedTours = visibleTours.filter((t) => !t.comingSoon);
	const completedCount = implementedTours.filter((t) => completedTourIds.has(t.id)).length;

	const renderTourItem = (tour: TourDefinition): JSX.Element => {
		const completed = completedTourIds.has(tour.id);
		return (
			<li key={tour.id}>
				<button
					id={`tsp-item-${tour.id}`}
					className="tsp-item"
					disabled={isTourActive || !!tour.comingSoon}
					onClick={tour.comingSoon ? undefined : (): void => void startTour(tour.id)}
				>
					<i
						id={`tsp-icon-${tour.id}`}
						className={`bi bi-check-circle ${completed ? "tsp-icon--done" : "tsp-icon"}`}
					/>
					<span className="tsp-item-title">{tour.title}</span>
					{tour.premium && <span className="tsp-badge tsp-badge--premium">Premium</span>}
					{tour.comingSoon && <span className="tsp-badge tsp-badge--soon">Soon</span>}
				</button>
			</li>
		);
	};

	if (!anchorRect) return null;

	return (
		<>
		<div
			className={`tsp-backdrop${isClosing ? " tsp-backdrop--closing" : ""}`}
			onClick={closeTourSelect}
		/>
		<div
			ref={panelRef}
			id="tsp-panel"
			className={`tsp-panel${isClosing ? " tsp-panel--closing" : ""}`}
			style={{ top: panelTop || anchorRect.top, left: anchorRect.right + 12 }}
			role="dialog"
			aria-label="Guided Tours"
		>
			<div className="tsp-header">
				<p className="tsp-heading">
					Guided Tours
					<span id="tsp-progress" className="tsp-progress">{completedCount}/{implementedTours.length}</span>
				</p>
				<button id="tsp-close-btn" className="tsp-close-btn" onClick={closeTourSelect} aria-label="Close">
					<i className="bi bi-x" />
				</button>
			</div>
			<ul
				className="tsp-list"
				style={{ gridTemplateRows: `repeat(${Math.ceil(implementedTours.length / 2)}, auto)` }}
			>
				{implementedTours.map((tour) => renderTourItem(tour))}
			</ul>
		</div>
		</>
	);
}
