import React, { JSX, useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useTour } from "../../contexts/TourContext";
import { TOUR_STEPS, TourStep } from "./tourSteps";
import "./GuidedTour.scss";

const SPOTLIGHT_PAD = 8;
const GAP = 16; // gap between spotlight edge and popover edge
const POP_W = 300;
const POP_MIN_H = 150;
const MARGIN = 12; // min distance from viewport edge

type Side = "top" | "bottom" | "left" | "right";

function bestSide(rect: DOMRect, preferred: Side): Side {
	const vw = window.innerWidth;
	const vh = window.innerHeight;
	const space: Record<Side, number> = {
		bottom: vh - rect.bottom - SPOTLIGHT_PAD - GAP,
		top: rect.top - SPOTLIGHT_PAD - GAP,
		right: vw - rect.right - SPOTLIGHT_PAD - GAP,
		left: rect.left - SPOTLIGHT_PAD - GAP,
	};

	// Use preferred if there's enough room
	const minH = POP_MIN_H;
	const minW = POP_W + MARGIN;
	const fits: Record<Side, boolean> = {
		bottom: space.bottom >= minH,
		top: space.top >= minH,
		right: space.right >= minW,
		left: space.left >= minW,
	};

	if (fits[preferred]) return preferred;

	// Fallback: pick side with most space (honouring axis preference)
	const axis = preferred === "top" || preferred === "bottom" ? "vertical" : "horizontal";
	if (axis === "vertical") {
		if (fits.bottom || fits.top) return space.bottom >= space.top ? "bottom" : "top";
		// No room on vertical — try horizontal
		return space.right >= space.left ? "right" : "left";
	} else {
		if (fits.right || fits.left) return space.right >= space.left ? "right" : "left";
		// No room on horizontal — try vertical
		return space.bottom >= space.top ? "bottom" : "top";
	}
}

function computePopoverStyle(rect: DOMRect, preferred: TourStep["placement"]): React.CSSProperties {
	if (preferred === "center") return {};

	const vw = window.innerWidth;
	const vh = window.innerHeight;
	const side = bestSide(rect, preferred as Side);

	let top: number | undefined;
	let bottom: number | undefined;
	let left: number | undefined;
	let right: number | undefined;
	let maxHeight: number;

	if (side === "bottom") {
		top = rect.bottom + SPOTLIGHT_PAD + GAP;
		left = Math.min(Math.max(rect.left, MARGIN), vw - POP_W - MARGIN);
		maxHeight = vh - top - MARGIN;
	} else if (side === "top") {
		const anchorBottom = rect.top - SPOTLIGHT_PAD - GAP;
		maxHeight = anchorBottom - MARGIN;
		bottom = vh - anchorBottom;
		left = Math.min(Math.max(rect.left, MARGIN), vw - POP_W - MARGIN);
	} else if (side === "right") {
		left = rect.right + SPOTLIGHT_PAD + GAP;
		top = Math.min(Math.max(rect.top, MARGIN), vh - POP_MIN_H - MARGIN);
		maxHeight = vh - top - MARGIN;
	} else {
		// left
		right = vw - (rect.left - SPOTLIGHT_PAD - GAP);
		top = Math.min(Math.max(rect.top, MARGIN), vh - POP_MIN_H - MARGIN);
		maxHeight = vh - top - MARGIN;
	}

	return { top, bottom, left, right, maxHeight: Math.max(maxHeight, POP_MIN_H) };
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
	const { isTourActive, endTour, isCleaningUp } = useTour();
	const navigate = useNavigate();
	const location = useLocation();

	const [step, setStep] = useState<number>(0);
	const [targetRect, setTargetRect] = useState<DOMRect | null>(null);

	const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
	const rafRef = useRef<number | null>(null);
	const waitPollRef = useRef<ReturnType<typeof setInterval> | null>(null);
	const autoFillCleanupRef = useRef<(() => void) | null>(null);
	const locationRef = useRef(location.pathname);

	locationRef.current = location.pathname;

	const stopPoll = useCallback(() => {
		if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
	}, []);

	const stopRaf = useCallback(() => {
		if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = null; }
	}, []);

	const stopWait = useCallback(() => {
		if (waitPollRef.current) { clearInterval(waitPollRef.current); waitPollRef.current = null; }
		autoFillCleanupRef.current?.();
		autoFillCleanupRef.current = null;
	}, []);

	const advanceToStep = useCallback(
		(targetStep: number): void => {
			stopPoll(); stopRaf(); stopWait();
			setTargetRect(null);
			if (targetStep >= TOUR_STEPS.length) { void endTour(true); return; }
			setStep(targetStep);
		},
		[stopPoll, stopRaf, stopWait, endTour]
	);

	// ── Find target element, then track it with RAF ─────────────────────────
	useEffect(() => {
		if (!isTourActive) return;
		const stepDef = TOUR_STEPS[step];
		if (!stepDef?.targetSelector) { setTargetRect(null); return; }

		if (stepDef.route) {
			const path = stepDef.route.replace("/jam", "");
			if (locationRef.current !== path) navigate(path);
		}

		// Poll until the element appears (with non-zero dimensions)
		let elapsed = 0;
		pollRef.current = setInterval(() => {
			const el = document.querySelector<HTMLElement>(stepDef.targetSelector!);
			const r = el?.getBoundingClientRect();
			if (r && r.width > 0 && r.height > 0) {
				stopPoll();
				// Short delay so Bootstrap modal animation has time to settle
				setTimeout(() => {
					const el2 = document.querySelector<HTMLElement>(stepDef.targetSelector!);
					if (!el2) return;
					setTargetRect(el2.getBoundingClientRect());

					// RAF loop keeps rect in sync with any ongoing animation / scroll
					const trackRect = () => {
						const el3 = document.querySelector<HTMLElement>(stepDef.targetSelector!);
						if (!el3) return;
						const newR = el3.getBoundingClientRect();
						setTargetRect(prev => {
							if (prev && prev.top === newR.top && prev.left === newR.left &&
								prev.width === newR.width && prev.height === newR.height) return prev;
							return newR;
						});
						rafRef.current = requestAnimationFrame(trackRect);
					};
					rafRef.current = requestAnimationFrame(trackRect);
				}, 350);
			} else {
				elapsed += 50;
				if (elapsed >= 3000) { stopPoll(); setStep(s => s + 1); }
			}
		}, 50);

		return () => { stopPoll(); stopRaf(); };
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
				retryTimer = setInterval(() => { if (attach()) clearInterval(retryTimer); }, 50);
				const timeout = setTimeout(() => clearInterval(retryTimer), 5000);
				autoFillCleanupRef.current = () => {
					clearInterval(retryTimer); clearTimeout(timeout); cleanup?.();
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
			if (met) { stopWait(); setStep(s => s + 1); }
		}, 50);

		return stopWait;
	}, [step, isTourActive, stopWait]);

	// ── Escape key ───────────────────────────────────────────────────────────
	useEffect(() => {
		if (!isTourActive) return;
		const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") void endTour(false); };
		window.addEventListener("keydown", onKey);
		return () => window.removeEventListener("keydown", onKey);
	}, [isTourActive, endTour]);

	// ── Reset on tour start ──────────────────────────────────────────────────
	useEffect(() => { if (isTourActive) setStep(0); }, [isTourActive]);

	if (!isTourActive) return null;
	const currentStep = TOUR_STEPS[step];
	if (!currentStep) return null;

	const showNext = !currentStep.hideNextButton;
	const isFirst = step === 0;
	const isLast = step === TOUR_STEPS.length - 1;
	const popoverStyle = targetRect ? computePopoverStyle(targetRect, currentStep.placement) : {};

	return (
		<>
			{targetRect && (
				<div
					className="tour-spotlight"
					style={{
						top: targetRect.top - SPOTLIGHT_PAD,
						left: targetRect.left - SPOTLIGHT_PAD,
						width: targetRect.width + SPOTLIGHT_PAD * 2,
						height: targetRect.height + SPOTLIGHT_PAD * 2,
					}}
				/>
			)}
			<div
				key={step}
				className={`tour-popover${currentStep.placement === "center" ? " tour-popover-center" : ""}`}
				style={{ width: POP_W, ...popoverStyle }}
				role="dialog"
				aria-label={`Tour step ${step + 1} of ${TOUR_STEPS.length}: ${currentStep.title}`}
			>
				<div className="tour-popover-header">
					<span className="tour-step-counter">{step + 1} / {TOUR_STEPS.length}</span>
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
								onClick={() => isLast ? void endTour(true) : advanceToStep(step + 1)}
							>
								{isLast
									? isCleaningUp
										? <><span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />Cleaning up…</>
										: "Done"
									: "Next"}
							</button>
						)}
					</div>
				)}
			</div>
		</>
	);
}
