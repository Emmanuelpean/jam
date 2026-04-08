import React, { JSX, useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useTour } from "../../contexts/TourContext";

import { getTourById, TourStep } from "./tourSteps";
import "./GuidedTour.scss";

const SPOTLIGHT_PAD = 8;
const GAP = 14; // gap between spotlight edge and popover edge
const POP_W = 320;
const POP_MIN_H = 120;
const MARGIN = 16; // min distance from viewport edge

type Side = "top" | "bottom" | "left" | "right";
const OPPOSITE: Record<Side, Side> = { bottom: "top", top: "bottom", left: "right", right: "left" };
const ALL_SIDES: Side[] = ["bottom", "top", "right", "left"];

function bestSide(rect: DOMRect, preferred: Side): Side {
	const vw = window.innerWidth;
	const vh = window.innerHeight;
	const space: Record<Side, number> = {
		bottom: vh - rect.bottom - SPOTLIGHT_PAD - GAP,
		top: rect.top - SPOTLIGHT_PAD - GAP,
		right: vw - rect.right - SPOTLIGHT_PAD - GAP,
		left: rect.left - SPOTLIGHT_PAD - GAP,
	};
	const fits: Record<Side, boolean> = {
		bottom: space.bottom >= POP_MIN_H + MARGIN,
		top: space.top >= POP_MIN_H + MARGIN,
		right: space.right >= POP_W + MARGIN,
		left: space.left >= POP_W + MARGIN,
	};

	if (fits[preferred]) return preferred;
	if (fits[OPPOSITE[preferred]]) return OPPOSITE[preferred];

	// Try remaining sides sorted by available space
	const others = ALL_SIDES.filter((s) => s !== preferred && s !== OPPOSITE[preferred]);
	others.sort((a, b) => space[b] - space[a]);
	for (const s of others) {
		if (fits[s]) return s;
	}

	// Nothing fits — pick the side with the most space
	return ALL_SIDES.reduce((a, b) => (space[a] >= space[b] ? a : b));
}

function computePopoverStyle(rect: DOMRect, preferred: TourStep["placement"]): React.CSSProperties {
	if (preferred === "center") return {};

	const vw = window.innerWidth;
	const vh = window.innerHeight;
	const side = bestSide(rect, preferred as Side);

	// Center the popover on the target's relevant axis, clamped to viewport
	const leftCentered = Math.max(MARGIN, Math.min(
		rect.left + rect.width / 2 - POP_W / 2,
		vw - POP_W - MARGIN,
	));
	const topCentered = Math.max(MARGIN, Math.min(
		rect.top + rect.height / 2 - POP_MIN_H / 2,
		vh - POP_MIN_H - MARGIN,
	));

	switch (side) {
		case "bottom": {
			const top = rect.bottom + SPOTLIGHT_PAD + GAP;
			return { top, left: leftCentered, maxHeight: Math.max(vh - top - MARGIN, POP_MIN_H) };
		}
		case "top": {
			const cssBottom = vh - (rect.top - SPOTLIGHT_PAD - GAP);
			return {
				bottom: cssBottom,
				left: leftCentered,
				maxHeight: Math.max(rect.top - SPOTLIGHT_PAD - GAP - MARGIN, POP_MIN_H),
			};
		}
		case "right": {
			const left = Math.min(rect.right + SPOTLIGHT_PAD + GAP, vw - POP_W - MARGIN);
			return { left, top: topCentered, maxHeight: Math.max(vh - topCentered - MARGIN, POP_MIN_H) };
		}
		case "left": {
			const left = Math.max(MARGIN, rect.left - SPOTLIGHT_PAD - GAP - POP_W);
			return { left, top: topCentered, maxHeight: Math.max(vh - topCentered - MARGIN, POP_MIN_H) };
		}
	}
}

/** Force a value into a React-controlled input */
function setNativeInputValue(el: HTMLInputElement, value: string): void {
	const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
	if (nativeSetter) {
		nativeSetter.call(el, value);
		el.dispatchEvent(new Event("input", { bubbles: true }));
		el.dispatchEvent(new Event("change", { bubbles: true }));
	}
}

export function GuidedTour(): JSX.Element | null {
	const { isTourActive, activeTourId, endTour, isCleaningUp } = useTour();
	const navigate = useNavigate();
	const location = useLocation();

	const TOUR_STEPS = activeTourId ? (getTourById(activeTourId)?.steps ?? []) : [];

	const [step, setStep] = useState<number>(0);
	const [targetRect, setTargetRect] = useState<DOMRect | null>(null);

	const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
	const rafRef = useRef<number | null>(null);
	const waitPollRef = useRef<ReturnType<typeof setInterval> | null>(null);
	const autoFillCleanupRef = useRef<(() => void) | null>(null);
	const locationRef = useRef(location.pathname);

	locationRef.current = location.pathname;

	const stopPoll = useCallback(() => {
		if (pollRef.current) {
			clearInterval(pollRef.current);
			pollRef.current = null;
		}
	}, []);

	const stopRaf = useCallback(() => {
		if (rafRef.current) {
			cancelAnimationFrame(rafRef.current);
			rafRef.current = null;
		}
	}, []);

	const stopWait = useCallback(() => {
		if (waitPollRef.current) {
			clearInterval(waitPollRef.current);
			waitPollRef.current = null;
		}
		autoFillCleanupRef.current?.();
		autoFillCleanupRef.current = null;
	}, []);

	const advanceToStep = useCallback(
		(targetStep: number): void => {
			stopPoll();
			stopRaf();
			stopWait();
			setTargetRect(null);
			if (targetStep >= TOUR_STEPS.length) {
				void endTour(true);
				return;
			}
			setStep(targetStep);
		},
		[stopPoll, stopRaf, stopWait, endTour]
	);

	// ── Find target element, then track it with RAF ─────────────────────────
	useEffect(() => {
		if (!isTourActive) return;
		const stepDef = TOUR_STEPS[step];
		if (!stepDef?.targetId) {
			setTargetRect(null);
			return;
		}

		if (stepDef.route) {
			const path = stepDef.route.replace("/jam", "");
			if (locationRef.current !== path) navigate(path);
		}

		// Poll until the element appears (with non-zero dimensions)
		let elapsed = 0;
		pollRef.current = setInterval(() => {
			const el = document.getElementById(stepDef.targetId!);
			const r = el?.getBoundingClientRect();
			if (r && r.width > 0 && r.height > 0) {
				stopPoll();
				// Short delay so Bootstrap modal animation has time to settle
				setTimeout(() => {
					const el2 = document.getElementById(stepDef.targetId!);
					if (!el2) return;
					setTargetRect(el2.getBoundingClientRect());

					// RAF loop keeps rect in sync with any ongoing animation / scroll
					const trackRect = () => {
						const el3 = document.getElementById(stepDef.targetId!);
						if (!el3) return;
						const newR = el3.getBoundingClientRect();
						setTargetRect((prev) => {
							if (
								prev &&
								prev.top === newR.top &&
								prev.left === newR.left &&
								prev.width === newR.width &&
								prev.height === newR.height
							)
								return prev;
							return newR;
						});
						rafRef.current = requestAnimationFrame(trackRect);
					};
					rafRef.current = requestAnimationFrame(trackRect);
				}, 350);
			} else {
				elapsed += 50;
				if (elapsed >= 3000) {
					stopPoll();
					setStep((s) => s + 1);
				}
			}
		}, 50);

		return () => {
			stopPoll();
			stopRaf();
		};
	}, [step, isTourActive, navigate, stopPoll, stopRaf]);

	// ── Interactive: waitForSelector / waitForSelectorGone / waitForInput ───
	useEffect(() => {
		if (!isTourActive) return;
		const stepDef = TOUR_STEPS[step];
		if (!stepDef) return;
		const { waitForSelector, waitForSelectorGone, waitForInput, autoFill } = stepDef;
		if (!waitForSelector && !waitForSelectorGone && !waitForInput && !autoFill) return;

		// Auto-fill watcher
		if (autoFill) {
			let filled = false;
			let cleanup: (() => void) | null = null;
			let retryTimer: ReturnType<typeof setInterval>;

			const attach = (): boolean => {
				const watchEl = document.querySelector<HTMLInputElement>(autoFill.watchSelector);
				if (!watchEl) return false;
				const handler = () => {
					if (filled || !watchEl.value.trim()) return;
					const fillEl = document.querySelector<HTMLInputElement>(autoFill.fillSelector);
					if (fillEl && !fillEl.value.trim()) {
						filled = true;
						setNativeInputValue(fillEl, autoFill.fillValue);
					}
				};
				watchEl.addEventListener("input", handler);
				cleanup = () => watchEl.removeEventListener("input", handler);
				return true;
			};

			if (!attach()) {
				retryTimer = setInterval(() => {
					if (attach()) clearInterval(retryTimer);
				}, 50);
				const timeout = setTimeout(() => clearInterval(retryTimer), 5000);
				autoFillCleanupRef.current = () => {
					clearInterval(retryTimer);
					clearTimeout(timeout);
					cleanup?.();
				};
			} else {
				autoFillCleanupRef.current = () => cleanup?.();
			}
		}

		// Condition polling
		waitPollRef.current = setInterval(() => {
			let met = false;
			if (waitForSelector) {
				met = !!document.querySelector(waitForSelector);
			} else if (waitForSelectorGone) {
				met = !document.querySelector(waitForSelectorGone);
			} else if (waitForInput) {
				const el = document.querySelector<HTMLInputElement>(waitForInput);
				met = !!el && el.value.trim().length > 0;
			}
			if (met) {
				stopWait();
				setStep((s) => s + 1);
			}
		}, 50);

		return stopWait;
	}, [step, isTourActive, stopWait]);

	// ── Keyboard navigation ──────────────────────────────────────────────────
	const stepRef = useRef(step);
	stepRef.current = step;
	const tourStepsRef = useRef(TOUR_STEPS);
	tourStepsRef.current = TOUR_STEPS;

	useEffect(() => {
		if (!isTourActive) return;
		const onKey = (e: KeyboardEvent) => {
			// Don't hijack keys while the user is typing in an input/textarea
			const tag = (e.target as HTMLElement)?.tagName;
			const isTyping = tag === "INPUT" || tag === "TEXTAREA" || (e.target as HTMLElement)?.isContentEditable;

			if (e.key === "Escape") {
				void endTour(false);
				return;
			}

			if (isTyping) return;

			const steps = tourStepsRef.current;
			const s = stepRef.current;
			const showNext = !steps[s]?.hideNextButton;

			if ((e.key === "ArrowRight" || e.key === "Enter") && showNext && !isCleaningUp) {
				e.preventDefault();
				if (s >= steps.length - 1) void endTour(true);
				else advanceToStep(s + 1);
			} else if (e.key === "ArrowLeft" && s > 0 && showNext) {
				e.preventDefault();
				advanceToStep(s - 1);
			}
		};
		window.addEventListener("keydown", onKey);
		return () => window.removeEventListener("keydown", onKey);
	}, [isTourActive, endTour, advanceToStep, isCleaningUp]);

	// ── Reset on tour start ──────────────────────────────────────────────────
	useEffect(() => {
		if (isTourActive) setStep(0);
	}, [isTourActive]);

	if (!isTourActive) return null;
	const currentStep = TOUR_STEPS[step];
	if (!currentStep) return null;

	// Hide the popover (but keep the spotlight) while waiting for the target element.
	// Returning null here would unmount the spotlight and cause the backdrop to flicker.
	const waitingForTarget = currentStep.targetId != null && targetRect === null;

	const showNext = !currentStep.hideNextButton;
	const isFirst = step === 0;
	const isLast = step === TOUR_STEPS.length - 1;
	const popoverStyle = targetRect ? computePopoverStyle(targetRect, currentStep.placement) : {};

	return (
		<>
			<div
				className="tour-spotlight"
				style={targetRect ? {
					top: targetRect.top - SPOTLIGHT_PAD,
					left: targetRect.left - SPOTLIGHT_PAD,
					width: targetRect.width + SPOTLIGHT_PAD * 2,
					height: targetRect.height + SPOTLIGHT_PAD * 2,
				} : { top: -1, left: -1, width: 1, height: 1 }}
			/>
			{!waitingForTarget && <div
				key={step}
				className={`tour-popover${currentStep.placement === "center" ? " tour-popover-center" : ""}`}
				style={{ width: POP_W, ...popoverStyle }}
				role="dialog"
				aria-label={`Tour step ${step + 1} of ${TOUR_STEPS.length}: ${currentStep.title}`}
			>
				<div className="tour-popover-body">
					<div className="tour-popover-header">
						<span className="tour-step-counter">
							Step {step + 1} of {TOUR_STEPS.length}
						</span>
						<button className="tour-skip-btn" onClick={() => void endTour(false)}>
							Skip tour
						</button>
					</div>
					<h5 className="tour-popover-title">{currentStep.title}</h5>
					<p className="tour-popover-content">{currentStep.content}</p>
					{(showNext || !isFirst) && (
						<div className="tour-popover-footer">
							{!isFirst && showNext && (
								<button className="tour-btn-secondary" onClick={() => advanceToStep(step - 1)}>
									Back
								</button>
							)}
							{showNext && (
								<button
									className="tour-btn-primary"
									disabled={isCleaningUp}
									onClick={() => (isLast ? void endTour(true) : advanceToStep(step + 1))}
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
										"Next"
									)}
								</button>
							)}
						</div>
					)}
				</div>
			</div>}
		</>
	);
}
