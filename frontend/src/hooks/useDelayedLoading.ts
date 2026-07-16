import { useEffect, useRef, useState } from "react";

const SHOW_DELAY = 300;
const MIN_DISPLAY_MS = 500;

export const useDelayedLoading = (loading: boolean): boolean => {
	const [visibleLoading, setVisibleLoading] = useState(false);
	const shownAtRef = useRef<number | null>(null);

	useEffect(() => {
		if (loading) {
			const showTimer = setTimeout(() => {
				setVisibleLoading(true);
				shownAtRef.current = Date.now();
			}, SHOW_DELAY);
			return (): void => clearTimeout(showTimer);
		}

		if (shownAtRef.current === null) {
			setVisibleLoading(false);
			return;
		}

		const remaining: number = MIN_DISPLAY_MS - (Date.now() - shownAtRef.current);
		if (remaining <= 0) {
			setVisibleLoading(false);
			shownAtRef.current = null;
			return;
		}

		const hideTimer = setTimeout(() => {
			setVisibleLoading(false);
			shownAtRef.current = null;
		}, remaining);
		return (): void => clearTimeout(hideTimer);
	}, [loading]);

	return visibleLoading;
};
