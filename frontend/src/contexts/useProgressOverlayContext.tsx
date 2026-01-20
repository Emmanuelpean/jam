import React, {
	createContext,
	JSX,
	ReactNode,
	useContext,
	useEffect,
	useRef,
	useState,
} from "react";
import { ProgressOverlay } from "../components/ProgressOverlay/ProgressOverlay";

interface ProgressOverlayContextType {
	showProgress: (message?: string, title?: string) => void;
	hideProgress: () => void;
	isShowing: boolean;
}

const ProgressOverlayContext = createContext<ProgressOverlayContextType | undefined>(undefined);

interface ProgressOverlayProviderProps {
	children: ReactNode;
}
export const ProgressOverlayProvider: React.FC<ProgressOverlayProviderProps> = ({
	children,
}: ProgressOverlayProviderProps): JSX.Element => {
	const [show, setShow] = useState<boolean>(false);
	const [title, setTitle] = useState<string | undefined>(undefined);
	const [message, setMessage] = useState<string | React.ReactNode | undefined>(undefined);
	const showTimerRef = useRef<NodeJS.Timeout | null>(null);
	const hideTimerRef = useRef<NodeJS.Timeout | null>(null);
	const shownAtRef = useRef<number | null>(null);

	const showProgress = (message?: string, title?: string): void => {
		const SHOW_DELAY = 300; // Don't show overlay if operation completes within 300ms

		// Clear any pending hide
		if (hideTimerRef.current) {
			clearTimeout(hideTimerRef.current);
			hideTimerRef.current = null;
		}

		// Set up delayed show
		if (showTimerRef.current) {
			clearTimeout(showTimerRef.current);
		}

		setTitle(title);
		setMessage(message);

		showTimerRef.current = setTimeout(() => {
			setShow(true);
			shownAtRef.current = Date.now();
			showTimerRef.current = null;
		}, SHOW_DELAY);
	};

	const hideProgress = (): void => {
		const MIN_DISPLAY_TIME = 500; // Once shown, display for at least 500ms

		// Clear pending show - operation completed before delay
		if (showTimerRef.current) {
			clearTimeout(showTimerRef.current);
			showTimerRef.current = null;
			return; // Never showed, so don't need to hide
		}

		// If overlay is showing, ensure minimum display time
		if (shownAtRef.current) {
			const elapsed = Date.now() - shownAtRef.current;
			const remaining = MIN_DISPLAY_TIME - elapsed;

			if (remaining > 0) {
				hideTimerRef.current = setTimeout(() => {
					setShow(false);
					setTitle(undefined);
					setMessage(undefined);
					shownAtRef.current = null;
					hideTimerRef.current = null;
				}, remaining);
			} else {
				setShow(false);
				setTitle(undefined);
				setMessage(undefined);
				shownAtRef.current = null;
			}
		}
	};

	// Cleanup on unmount
	useEffect(() => {
		return () => {
			if (showTimerRef.current) clearTimeout(showTimerRef.current);
			if (hideTimerRef.current) clearTimeout(hideTimerRef.current);
		};
	}, []);

	return (
		<ProgressOverlayContext.Provider value={{ showProgress, hideProgress, isShowing: show }}>
			{children}
			<ProgressOverlay show={show} title={title} message={message} />
		</ProgressOverlayContext.Provider>
	);
};

export const useProgressOverlay = (): ProgressOverlayContextType => {
	const context = useContext(ProgressOverlayContext);
	if (!context) {
		throw new Error("useProgressOverlay must be used within a ProgressOverlayProvider");
	}
	return context;
};
