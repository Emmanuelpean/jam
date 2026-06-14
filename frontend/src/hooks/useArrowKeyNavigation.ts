import { useEffect, useRef } from "react";

interface UseArrowKeyNavigationOptions {
    active: boolean;
    onNext: () => void;
    onPrev: () => void;
    canGoPrev?: boolean;
    canGoNext?: boolean;
    skipWhenTyping?: boolean;
    onEscape?: () => void;
    nextOnEnter?: boolean;
}

export function useArrowKeyNavigation({
    active,
    onNext,
    onPrev,
    canGoPrev = true,
    canGoNext = true,
    skipWhenTyping = false,
    onEscape,
    nextOnEnter = false,
}: UseArrowKeyNavigationOptions): void {
    const onNextRef = useRef(onNext);
    onNextRef.current = onNext;
    const onPrevRef = useRef(onPrev);
    onPrevRef.current = onPrev;
    const canGoPrevRef = useRef(canGoPrev);
    canGoPrevRef.current = canGoPrev;
    const canGoNextRef = useRef(canGoNext);
    canGoNextRef.current = canGoNext;
    const onEscapeRef = useRef(onEscape);
    onEscapeRef.current = onEscape;

    useEffect(() => {
        if (!active) return;
        const onKey = (e: KeyboardEvent): void => {
            if (e.key === "Escape") {
                onEscapeRef.current?.();
                return;
            }
            if (skipWhenTyping) {
                const tag = (e.target as HTMLElement)?.tagName;
                if (tag === "INPUT" || tag === "TEXTAREA" || (e.target as HTMLElement)?.isContentEditable) return;
            }
            if ((e.key === "ArrowRight" || (nextOnEnter && e.key === "Enter")) && canGoNextRef.current) {
                e.preventDefault();
                onNextRef.current();
            } else if (e.key === "ArrowLeft" && canGoPrevRef.current) {
                e.preventDefault();
                onPrevRef.current();
            }
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [active, skipWhenTyping, nextOnEnter]);
}
