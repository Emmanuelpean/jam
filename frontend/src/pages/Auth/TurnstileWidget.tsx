import React, { JSX, useEffect, useRef } from "react";

declare global {
	interface Window {
		turnstile?: {
			render: (
				element: HTMLElement,
				options: {
					sitekey: string;
					callback?: (token: string) => void;
					"error-callback"?: () => void;
					"expired-callback"?: () => void;
					theme?: "light" | "dark" | "auto";
					action?: string;
				}
			) => string;
			reset: (widgetId?: string) => void;
			remove: (widgetId: string) => void;
		};
	}
}

const SCRIPT_SRC = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";

let scriptPromise: Promise<void> | null = null;

const loadTurnstileScript = (): Promise<void> => {
	if (typeof window === "undefined") return Promise.resolve();
	if (window.turnstile) return Promise.resolve();
	if (scriptPromise) return scriptPromise;

	scriptPromise = new Promise<void>((resolve, reject) => {
		const existing: HTMLScriptElement | null = document.querySelector(`script[src^="${SCRIPT_SRC}"]`);
		if (existing) {
			existing.addEventListener("load", () => resolve());
			existing.addEventListener("error", () => reject(new Error("Failed to load Turnstile script")));
			return;
		}
		const script: HTMLScriptElement = document.createElement("script");
		script.src = SCRIPT_SRC;
		script.async = true;
		script.defer = true;
		script.onload = () => resolve();
		script.onerror = () => reject(new Error("Failed to load Turnstile script"));
		document.head.appendChild(script);
	});

	return scriptPromise;
};

interface TurnstileWidgetProps {
	siteKey: string;
	onVerify: (token: string) => void;
	onExpire?: () => void;
	onError?: () => void;
	theme?: "light" | "dark" | "auto";
	action?: string;
}

export function TurnstileWidget({
	siteKey,
	onVerify,
	onExpire,
	onError,
	theme = "auto",
	action,
}: TurnstileWidgetProps): JSX.Element {
	const containerRef = useRef<HTMLDivElement>(null);
	const widgetIdRef = useRef<string | null>(null);
	const onVerifyRef = useRef(onVerify);
	const onExpireRef = useRef(onExpire);
	const onErrorRef = useRef(onError);

	useEffect(() => {
		onVerifyRef.current = onVerify;
		onExpireRef.current = onExpire;
		onErrorRef.current = onError;
	}, [onVerify, onExpire, onError]);

	useEffect(() => {
		let cancelled = false;

		loadTurnstileScript()
			.then(() => {
				if (cancelled || !containerRef.current || !window.turnstile) return;
				widgetIdRef.current = window.turnstile.render(containerRef.current, {
					sitekey: siteKey,
					theme,
					action,
					callback: (token: string) => onVerifyRef.current(token),
					"expired-callback": () => onExpireRef.current?.(),
					"error-callback": () => onErrorRef.current?.(),
				});
			})
			.catch(() => onErrorRef.current?.());

		return () => {
			cancelled = true;
			if (widgetIdRef.current && window.turnstile) {
				try {
					window.turnstile.remove(widgetIdRef.current);
				} catch {
					/* widget already gone */
				}
				widgetIdRef.current = null;
			}
		};
	}, [siteKey, theme, action]);

	return <div ref={containerRef} className="turnstile-widget" />;
}

export default TurnstileWidget;
