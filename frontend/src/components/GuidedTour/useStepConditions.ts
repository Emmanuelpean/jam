import { useCallback, useEffect, useRef, useState } from "react";
import { TourStep } from "./tourSteps";
import { setNativeInputValue } from "./tourUtils";

interface UseStepConditionsResult {
	inputValid: boolean;
	stop: () => void;
}

export function useStepConditions(
	step: number,
	isTourActive: boolean,
	stepDef: TourStep | undefined,
	onConditionMet: () => void,
): UseStepConditionsResult {
	const [inputValid, setInputValid] = useState(false);
	const waitPollRef = useRef<ReturnType<typeof setInterval> | null>(null);
	const autoFillCleanupRef = useRef<(() => void) | null>(null);
	const autoFocusedRef = useRef(false);
	const onConditionMetRef = useRef(onConditionMet);
	onConditionMetRef.current = onConditionMet;

	const stop = useCallback(() => {
		if (waitPollRef.current) { clearInterval(waitPollRef.current); waitPollRef.current = null; }
		autoFillCleanupRef.current?.();
		autoFillCleanupRef.current = null;
	}, []);

	useEffect(() => {
		setInputValid(!!stepDef?.waitForValidEmailIfFilled);
		autoFocusedRef.current = false;
	}, [step, stepDef?.waitForValidEmailIfFilled]);

	useEffect(() => {
		if (!isTourActive || !stepDef?.autoFocusSelector) return;
		const selector = stepDef.autoFocusSelector;
		const timer = setInterval(() => {
			const el = document.querySelector<HTMLInputElement>(selector);
			if (el) { clearInterval(timer); el.focus(); }
		}, 50);
		const timeout = setTimeout(() => clearInterval(timer), 3000);
		return () => { clearInterval(timer); clearTimeout(timeout); };
	}, [step, isTourActive, stepDef?.autoFocusSelector]);

	useEffect(() => {
		if (!isTourActive || !stepDef) return stop;
		const { waitForSelector, waitForSelectorGone, waitForInput, waitForValidEmailIfFilled, autoFill } = stepDef;
		if (!waitForSelector && !waitForSelectorGone && !waitForInput && !waitForValidEmailIfFilled && !autoFill) return stop;

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
				autoFillCleanupRef.current = () => { clearInterval(retryTimer); clearTimeout(timeout); cleanup?.(); };
			} else {
				autoFillCleanupRef.current = () => cleanup?.();
			}
		}

		const tryAutoFocus = (el: HTMLInputElement | null): void => {
			if (!el || autoFocusedRef.current || el.classList.contains("jam-select__input")) return;
			autoFocusedRef.current = true;
			el.focus();
		};

		waitPollRef.current = setInterval(() => {
			if (waitForValidEmailIfFilled) {
				const el = document.querySelector<HTMLInputElement>(waitForValidEmailIfFilled);
				tryAutoFocus(el);
				const value = el?.value.trim() ?? "";
				setInputValid(value === "" || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value));
				return;
			}
			if (waitForInput) {
				const el = document.querySelector<HTMLInputElement>(waitForInput);
				tryAutoFocus(el);
				if (!el) {
					setInputValid(false);
				} else if (el.classList.contains("jam-select__input")) {
					const container = el.closest(".jam-select");
					setInputValid(!!container?.querySelector(".jam-select__single-value, .jam-select__tag"));
				} else {
					setInputValid(el.value.trim().length > 0);
				}
				return;
			}
			let met = false;
			if (waitForSelector) met = !!document.querySelector(waitForSelector);
			else if (waitForSelectorGone) met = !document.querySelector(waitForSelectorGone);
			if (met) { stop(); onConditionMetRef.current(); }
		}, 50);

		return stop;
	}, [step, isTourActive, stepDef, stop]);

	return { inputValid, stop };
}
