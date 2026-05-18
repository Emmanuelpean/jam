import { MutableRefObject, useCallback, useEffect, useRef, useState } from "react";
import { expandTargetId, isClippedByScroll, rectEqual, resolveTarget } from "./tourUtils";

interface UseTrackTargetResult {
	targetRect: DOMRect | null;
	spotlightRect: DOMRect | null;
	stop: () => void;
}

export function useTrackTarget(
	step: number,
	isTourActive: boolean,
	targetId: string | null | undefined,
	demoJobId: number | null,
	demoScrapedJobId: number | null,
	demoScrapingFilterId: number | null,
	demoJobEmailId: number | null,
	directionRef: MutableRefObject<1 | -1>,
	onTargetNotFound: () => void,
): UseTrackTargetResult {
	const [targetRect, setTargetRect] = useState<DOMRect | null>(null);
	const [spotlightRect, setSpotlightRect] = useState<DOMRect | null>(null);
	const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
	const rafRef = useRef<number | null>(null);
	const onTargetNotFoundRef = useRef(onTargetNotFound);
	onTargetNotFoundRef.current = onTargetNotFound;

	const stop = useCallback(() => {
		if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
		if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = null; }
	}, []);

	useEffect(() => {
		if (!isTourActive || !targetId) {
			setTargetRect(null);
			return stop;
		}

		const resolvedId = expandTargetId(targetId, demoJobId, demoScrapedJobId, demoScrapingFilterId, demoJobEmailId);
		let elapsed = 0;

		pollRef.current = setInterval(() => {
			const el = resolveTarget(resolvedId);
			const r = el?.getBoundingClientRect();
			if (r && r.width > 0 && r.height > 0) {
				stop();
				if (isClippedByScroll(el!)) el!.scrollIntoView({ behavior: "smooth", block: "nearest" });
				setTargetRect(r);
				setSpotlightRect(r);

				const trackRect = () => {
					const tracked = resolveTarget(resolvedId);
					if (!tracked) return;
					const newR = tracked.getBoundingClientRect();
					setTargetRect((prev) => (prev && rectEqual(prev, newR) ? prev : newR));
					setSpotlightRect((prev) => (prev && rectEqual(prev, newR) ? prev : newR));
					rafRef.current = requestAnimationFrame(trackRect);
				};
				rafRef.current = requestAnimationFrame(trackRect);
			} else {
				elapsed += 50;
				if (elapsed >= 3000) { stop(); onTargetNotFoundRef.current(); }
			}
		}, 50);

		return stop;
	}, [step, isTourActive, targetId, demoJobId, demoScrapedJobId, demoScrapingFilterId, demoJobEmailId, stop]);

	return { targetRect, spotlightRect, stop };
}
