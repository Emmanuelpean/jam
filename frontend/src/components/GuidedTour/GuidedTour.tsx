import React, { JSX, useCallback, useEffect, useRef, useState } from "react";
import { useArrowKeyNavigation } from "../../hooks/useArrowKeyNavigation";
import { useNavigate, useLocation } from "react-router-dom";
import { useTour } from "../../contexts/TourContext";
import { useAuth } from "../../contexts/AuthContext";
import { getTourById, TOURS, TourStep } from "./tourSteps";
import { computePopoverStyle, POP_W, POP_W_LAST, SPOTLIGHT_PAD } from "./tourPositioning";
import { expandTargetId, resolveTarget } from "./tourUtils";
import { useTrackTarget } from "./useTrackTarget";
import { useStepConditions } from "./useStepConditions";
import "./GuidedTour.scss";

export function GuidedTour(): JSX.Element | null {
	const {
		isTourActive,
		activeTourId,
		endTour,
		endTourAndContinue,
		isCleaningUp,
		hasUserCreatedData,
		demoJobId,
		demoScrapedJobId,
		demoJobEmailId,
		demoScrapingFilterId,
		setAllowedContextMenuActions,
	} = useTour();
	const { currentUser } = useAuth();
	const isPremium = currentUser?.premium.is_active ?? false;
	const visibleTours = TOURS.filter(
		(t) => !t.comingSoon && (isPremium || !["import-scraped-job", "scraping-filters"].includes(t.id))
	);
	const currentTourIndex = visibleTours.findIndex((t) => t.id === activeTourId);
	const nextTour = currentTourIndex !== -1 ? visibleTours[currentTourIndex + 1] : undefined;
	const noKeepData = activeTourId ? (getTourById(activeTourId)?.noKeepData ?? false) : false;
	const navigate = useNavigate();
	const location = useLocation();

	const TOUR_STEPS: TourStep[] = activeTourId ? (getTourById(activeTourId)?.steps ?? []) : [];
	const tourStepsRef = useRef(TOUR_STEPS);
	tourStepsRef.current = TOUR_STEPS;

	const [step, setStep] = useState(0);
	const stepRef = useRef(step);
	stepRef.current = step;

	const [keepData, setKeepData] = useState(false);

	const directionRef = useRef<1 | -1>(1);

	// Stable refs so advanceToStep can call stop without depending on hook return values
	const stopTrackRef = useRef<() => void>(() => {});
	const stopConditionsRef = useRef<() => void>(() => {});

	// ── Step navigation ─────────────────────────────────────────────────────────
	const advanceToStep = useCallback(
		(targetStep: number): void => {
			stopTrackRef.current();
			stopConditionsRef.current();
			if (targetStep >= tourStepsRef.current.length) {
				void endTour(true);
				return;
			}
			directionRef.current = targetStep >= stepRef.current ? 1 : -1;
			setStep(targetStep);
		},
		[endTour]
	);

	const advanceFromCurrentStep = useCallback((): void => {
		const steps = tourStepsRef.current;
		const nextId = steps[stepRef.current]?.nextStepId;
		if (nextId) {
			const idx = steps.findIndex((s) => s.id === nextId);
			if (idx !== -1) {
				advanceToStep(idx);
				return;
			}
		}
		advanceToStep(stepRef.current + 1);
	}, [advanceToStep]);

	const advanceToStepById = useCallback(
		(stepId: string): void => {
			const idx = TOUR_STEPS.findIndex((s) => s.id === stepId);
			if (idx !== -1) advanceToStep(idx);
		},
		[advanceToStep, TOUR_STEPS]
	);

	// ── Target tracking ─────────────────────────────────────────────────────────
	const stepDef = TOUR_STEPS[step];

	const {
		targetRect,
		spotlightRect,
		stop: stopTrack,
	} = useTrackTarget(
		step,
		isTourActive,
		stepDef?.targetId,
		demoJobId,
		demoScrapedJobId,
		demoScrapingFilterId,
		demoJobEmailId,
		directionRef,
		() => setStep((s) => s + directionRef.current)
	);
	stopTrackRef.current = stopTrack;

	// ── Condition watching ───────────────────────────────────────────────────────
	const onConditionMet = useCallback((): void => {
		const steps = tourStepsRef.current;
		const autoStepId = steps[stepRef.current]?.autoAdvanceStepId;
		if (autoStepId) {
			const idx = steps.findIndex((s) => s.id === autoStepId);
			if (idx !== -1) {
				advanceToStep(idx);
				return;
			}
		}
		advanceFromCurrentStep();
	}, [advanceToStep, advanceFromCurrentStep]);

	const { inputValid, stop: stopConditions } = useStepConditions(step, isTourActive, stepDef, onConditionMet, directionRef);
	stopConditionsRef.current = stopConditions;

	const [hasVisibleErrors, setHasVisibleErrors] = useState(false);
	useEffect(() => {
		if (!isTourActive) { setHasVisibleErrors(false); return; }
		const id = setInterval(() => {
			setHasVisibleErrors(document.querySelector(".invalid-feedback.d-block:not(:empty)") !== null);
		}, 100);
		return () => clearInterval(id);
	}, [isTourActive]);

	// ── Route navigation — fires on step entry only, not on every pathname change ──
	useEffect(() => {
		if (!isTourActive || !stepDef?.route) return;
		const path = stepDef.route.replace("/jam", "");
		if (location.pathname !== path) navigate(path);
	}, [step, isTourActive]);

	// ── Auto-click (e.g. switch a tab) when a step becomes active ────────────────
	useEffect(() => {
		if (!isTourActive || !stepDef?.clickSelector) return;
		const el = resolveTarget(stepDef.clickSelector);
		(el as HTMLElement)?.click();
	}, [step, isTourActive, stepDef?.clickSelector]);

	// ── Skip step when its target element is absent (e.g. conditional form fields) ─
	useEffect(() => {
		if (!isTourActive || !stepDef?.skipIfSelectorAbsent) return;
		if (!document.querySelector(stepDef.skipIfSelectorAbsent)) {
			if (directionRef.current === 1) advanceFromCurrentStep();
			else advanceToStep(step - 1);
		}
	}, [step, isTourActive, stepDef?.skipIfSelectorAbsent, advanceFromCurrentStep, advanceToStep]);

	// ── Sync allowed context menu actions to TourContext ────────────────────────
	useEffect(() => {
		setAllowedContextMenuActions(stepDef?.allowedContextMenuActions ?? null);
		return () => setAllowedContextMenuActions(null);
	}, [step, isTourActive, stepDef, setAllowedContextMenuActions]);

	// ── Block left-clicks on the target (allows right-click for context menus) ──
	useEffect(() => {
		if (!isTourActive || !stepDef?.blockLeftClick || !stepDef.targetId) return;
		const resolvedId = expandTargetId(
			stepDef.targetId,
			demoJobId,
			demoScrapedJobId,
			demoScrapingFilterId,
			demoJobEmailId
		);
		const handler = (e: MouseEvent): void => {
			if (e.button !== 0) return;
			const el = resolveTarget(resolvedId);
			if (el && el.contains(e.target as Node)) {
				e.preventDefault();
				e.stopPropagation();
			}
		};
		document.addEventListener("mousedown", handler, true);
		document.addEventListener("click", handler, true);
		return () => {
			document.removeEventListener("mousedown", handler, true);
			document.removeEventListener("click", handler, true);
		};
	}, [isTourActive, step, stepDef, demoJobId, demoScrapedJobId, demoJobEmailId, demoScrapingFilterId]);

	// ── Keyboard navigation ──────────────────────────────────────────────────────
	const isLast = step === TOUR_STEPS.length - 1;
	const showNext = !stepDef?.hideNextButton;
	const nextDisabled =
		isCleaningUp ||
		hasVisibleErrors ||
		((!!stepDef?.waitForInput || !!stepDef?.waitForValidEmailIfFilled || !!stepDef?.waitForValidLinkedInIfFilled) &&
			!inputValid);
	const canGoBack =
		!isLast &&
		step > 0 &&
		(showNext || !!stepDef?.showBack) &&
		(!!stepDef?.showBack || !TOUR_STEPS[step - 1]?.hideNextButton);

	const isLastRef = useRef(isLast);
	isLastRef.current = isLast;
	const showNextRef = useRef(showNext);
	showNextRef.current = showNext;
	const nextDisabledRef = useRef(nextDisabled);
	nextDisabledRef.current = nextDisabled;
	const keepDataRef = useRef(keepData);
	keepDataRef.current = keepData;
	const hasUserCreatedDataRef = useRef(hasUserCreatedData);
	hasUserCreatedDataRef.current = hasUserCreatedData;

	useArrowKeyNavigation({
		active: isTourActive,
		onNext: () =>
			isLast
				? void endTour(true, noKeepData ? true : hasUserCreatedData ? keepData : undefined)
				: advanceFromCurrentStep(),
		onPrev: () => advanceToStep(step - 1),
		canGoPrev: canGoBack,
		canGoNext: showNext && !isCleaningUp && !nextDisabled,
		skipWhenTyping: true,
		onEscape: () => void endTour(false),
	});

	// ── Block Tab; bind Enter to the Next button ─────────────────────────────────
	useEffect(() => {
		if (!isTourActive) return;
		const handler = (e: KeyboardEvent): void => {
			if (e.key === "Tab") {
				e.preventDefault();
				return;
			}
			if (e.key === "Enter") {
				e.preventDefault();
				if (!showNextRef.current || nextDisabledRef.current) return;
				const def = tourStepsRef.current[stepRef.current];
				if (def?.nextActionSelector) {
					const el = document.querySelector(def.nextActionSelector);
					if (el instanceof HTMLElement) el.click();
				}
				isLastRef.current
					? void endTour(
							true,
							noKeepData ? true : hasUserCreatedDataRef.current ? keepDataRef.current : undefined
						)
					: advanceFromCurrentStep();
			}
		};
		document.addEventListener("keydown", handler, true);
		return () => document.removeEventListener("keydown", handler, true);
	}, [isTourActive, endTour, advanceFromCurrentStep]);

	// ── Reset on tour start ──────────────────────────────────────────────────────
	useEffect(() => {
		if (isTourActive) setStep(0);
	}, [isTourActive]);

	// ── Render ───────────────────────────────────────────────────────────────────
	if (!isTourActive || !stepDef) return null;

	const waitingForTarget = stepDef.targetId != null && targetRect === null;
	const popoverStyle = targetRect ? computePopoverStyle(targetRect, stepDef.placement) : {};

	return (
		<>
			{/* Blocking overlays — prevent interaction outside the targeted element */}
			{stepDef.targetId != null && spotlightRect ? (
				<>
					<div
						className="tour-block"
						style={{ top: 0, left: 0, right: 0, height: spotlightRect.top - SPOTLIGHT_PAD }}
					/>
					<div
						className="tour-block"
						style={{ top: spotlightRect.bottom + SPOTLIGHT_PAD, left: 0, right: 0, bottom: 0 }}
					/>
					<div
						className="tour-block"
						style={{
							top: spotlightRect.top - SPOTLIGHT_PAD,
							left: 0,
							width: spotlightRect.left - SPOTLIGHT_PAD,
							height: spotlightRect.height + SPOTLIGHT_PAD * 2,
						}}
					/>
					<div
						className="tour-block"
						style={{
							top: spotlightRect.top - SPOTLIGHT_PAD,
							left: spotlightRect.right + SPOTLIGHT_PAD,
							right: 0,
							height: spotlightRect.height + SPOTLIGHT_PAD * 2,
						}}
					/>
				</>
			) : stepDef.targetId == null ? (
				<div className="tour-block" style={{ top: 0, left: 0, right: 0, bottom: 0 }} />
			) : null}

			<div
				className="tour-spotlight"
				style={{
					opacity: stepDef.targetId != null && spotlightRect ? 1 : 0,
					...(spotlightRect
						? {
								top: spotlightRect.top - SPOTLIGHT_PAD,
								left: spotlightRect.left - SPOTLIGHT_PAD,
								width: spotlightRect.width + SPOTLIGHT_PAD * 2,
								height: spotlightRect.height + SPOTLIGHT_PAD * 2,
							}
						: { top: "50vh", left: "50vw", width: 0, height: 0 }),
				}}
			/>
			<div id="tour-backdrop" className="tour-backdrop" style={{ opacity: stepDef.targetId == null ? 1 : 0 }} />

			{!waitingForTarget && (
				<div
					key={step}
					id="tour-popover"
					className={`tour-popover${stepDef.placement === "center" ? " tour-popover-center" : ""}`}
					style={{ width: isLast ? POP_W_LAST : POP_W, ...popoverStyle }}
					role="dialog"
					aria-label={`Tour step ${step + 1} of ${TOUR_STEPS.length}: ${stepDef.title}`}
				>
					<div className="tour-popover-body">
						<div className="tour-popover-header">
							<span id="tour-step-counter" className="tour-step-counter">
								Step {step + 1} of {TOUR_STEPS.length}
							</span>
							<button id="tour-skip-btn" className="tour-skip-btn" onClick={() => void endTour(false)}>
								Skip tour
							</button>
						</div>
						<h5 id="tour-popover-title" className="tour-popover-title">
							{stepDef.title}
						</h5>
						<p className="tour-popover-content">{stepDef.content}</p>

						{stepDef.choices && (
							<div className="tour-choices">
								{stepDef.choices.map((choice) => (
									<button
										key={choice.targetStepId}
										id={`tour-choice-${choice.targetStepId}`}
										className="tour-choice-btn"
										onClick={() => advanceToStepById(choice.targetStepId)}
									>
										<i className={`bi ${choice.icon} me-2`} />
										{choice.label}
									</button>
								))}
							</div>
						)}

						{(showNext || canGoBack) && (
							<div className="tour-popover-footer">
								{isLast && hasUserCreatedData && !noKeepData && (
									<div className="form-check form-switch mb-0 me-auto">
										<input
											className="form-check-input"
											type="checkbox"
											id="tour-keep-data"
											checked={keepData}
											onChange={(e) => setKeepData(e.target.checked)}
										/>
										<label className="form-check-label" htmlFor="tour-keep-data">
											Keep my data
										</label>
									</div>
								)}
								{canGoBack && (
									<button
										id="tour-back-btn"
										className="tour-btn-secondary"
										onClick={() => {
											stopConditionsRef.current();
											const doNav = () => {
												stepDef.backStepId
													? advanceToStepById(stepDef.backStepId)
													: advanceToStep(step - 1);
											};
											if (stepDef.backActionSelector) {
												const el = document.querySelector(stepDef.backActionSelector);
												if (el instanceof HTMLElement) el.click();
												// Defer navigation so React finishes processing the DOM change
												// (e.g. modal close) before the new step's conditions start.
												setTimeout(doNav, 0);
											} else {
												doNav();
											}
										}}
									>
										<i className="bi bi-arrow-left me-1"></i>Back
									</button>
								)}
								{showNext && (
									<>
										{isLast && !isCleaningUp && nextTour && (
											<button
												id="tour-start-next-btn"
												className="tour-btn-secondary"
												onClick={() =>
													endTourAndContinue(
														nextTour.id,
														noKeepData ? true : hasUserCreatedData ? keepData : undefined
													)
												}
											>
												{nextTour.title} <i className="bi bi-arrow-right ms-1"></i>
											</button>
										)}
										<button
											id="tour-next-btn"
											className="tour-btn-primary"
											disabled={nextDisabled}
											onClick={() => {
												if (stepDef.nextActionSelector) {
													const el = document.querySelector(stepDef.nextActionSelector);
													if (el instanceof HTMLElement) el.click();
												}
												isLast
													? void endTour(
															true,
															noKeepData
																? true
																: hasUserCreatedData
																	? keepData
																	: undefined
														)
													: advanceFromCurrentStep();
											}}
										>
											{isLast ? (
												isCleaningUp ? (
													<>
														<span
															className="spinner-border spinner-border-sm me-2"
															role="status"
															aria-hidden="true"
														/>
														Cleaning up…
													</>
												) : (
													"Done"
												)
											) : (
												<>
													Next <i className="bi bi-arrow-right"></i>
												</>
											)}
										</button>
									</>
								)}
							</div>
						)}
					</div>
				</div>
			)}
		</>
	);
}
