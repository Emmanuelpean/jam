import { useEffect, useRef, useState } from "react";

const SHOW_DELAY = 300;
const MIN_DISPLAY_MS = 500;

export const useDelayedLoading = (loading: boolean): boolean => {
	const [visibleLoading, setVisibleLoading] = useState(false);
	const showTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
	const hideTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
	const shownAtRef = useRef<number | null>(null);

	useEffect(() => {
		if (loading) {
			if (hideTimerRef.current) {
				clearTimeout(hideTimerRef.current);
				hideTimerRef.current = null;
			}
			showTimerRef.current = setTimeout(() => {
				setVisibleLoading(true);
				shownAtRef.current = Date.now();
				showTimerRef.current = null;
			}, SHOW_DELAY);
		} else {
			if (showTimerRef.current) {
				clearTimeout(showTimerRef.current);
				showTimerRef.current = null;
				return;
			}
			if (shownAtRef.current) {
				const elapsed = Date.now() - shownAtRef.current;
				const remaining = MIN_DISPLAY_MS - elapsed;
				if (remaining > 0) {
					hideTimerRef.current = setTimeout(() => {
						setVisibleLoading(false);
						shownAtRef.current = null;
						hideTimerRef.current = null;
					}, remaining);
				} else {
					setVisibleLoading(false);
					shownAtRef.current = null;
				}
			}
		}
		return () => {
			if (showTimerRef.current) clearTimeout(showTimerRef.current);
			if (hideTimerRef.current) clearTimeout(hideTimerRef.current);
		};
	}, [loading]);

	return visibleLoading;
};
