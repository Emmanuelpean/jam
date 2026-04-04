import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

const ROUTES: Record<string, string> = {
	d: "/dashboard", D: "/dashboard",
	j: "/jobs",      J: "/jobs",
	p: "/persons",   P: "/persons",
	c: "/companies", C: "/companies",
	i: "/interviews", I: "/interviews",
	s: "/settings",  S: "/settings",
	a: "/aggregators", A: "/aggregators",
	k: "/keywords",  K: "/keywords",
	l: "/locations", L: "/locations",
	n: "/jobs",      N: "/jobs",
	v: "/speculative-applications", V: "/speculative-applications",
	u: "/job-application-updates",  U: "/job-application-updates",
};

function isTypingTarget(el: Element | null): boolean {
	if (!el) return false;
	const tag = el.tagName.toLowerCase();
	return tag === "input" || tag === "textarea" || tag === "select" || (el as HTMLElement).isContentEditable;
}

export function useCommandPalette(): { isOpen: boolean; close: () => void } {
	const { isAuthenticated } = useAuth();
	const navigate = useNavigate();
	const [isOpen, setIsOpen] = useState(false);
	const pendingJRef = useRef(false);
	const jTimeoutRef = useRef<ReturnType<typeof setTimeout>>();
	const lastShiftRef = useRef(0);

	useEffect(() => {
		const handleKeyDown = (e: KeyboardEvent): void => {
			if (e.key === "k" && (e.ctrlKey || e.metaKey)) {
				e.preventDefault();
				setIsOpen((o) => !o);
				return;
			}

			if (e.key === "Shift" && !e.ctrlKey && !e.altKey && !e.metaKey && !e.repeat) {
				const now = Date.now();
				if (now - lastShiftRef.current < 300) {
					e.preventDefault();
					setIsOpen((o) => !o);
					lastShiftRef.current = 0;
				} else {
					lastShiftRef.current = now;
				}
				return;
			}

			if (!isAuthenticated) return;
			if (isTypingTarget(document.activeElement)) return;
			if (isOpen) return;

			if (e.key === "j" || e.key === "J") {
				clearTimeout(jTimeoutRef.current);
				pendingJRef.current = true;
				jTimeoutRef.current = setTimeout(() => {
					pendingJRef.current = false;
				}, 500);
				return;
			}

			if (pendingJRef.current) {
				clearTimeout(jTimeoutRef.current);
				pendingJRef.current = false;
				const route = ROUTES[e.key];
				if (route) {
					const state = e.key === "n" || e.key === "N" ? { quickAdd: true } : undefined;
					navigate(route, state ? { state } : undefined);
				}
			}
		};

		window.addEventListener("keydown", handleKeyDown);
		return () => window.removeEventListener("keydown", handleKeyDown);
	}, [isAuthenticated, isOpen, navigate]);

	return { isOpen, close: () => setIsOpen(false) };
}
