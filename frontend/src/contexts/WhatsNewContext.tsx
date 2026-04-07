import React, { createContext, JSX, ReactNode, useCallback, useContext, useEffect, useRef, useState } from "react";
import { useAuth } from "./AuthContext";
import { useTour } from "./TourContext";
import { WhatsNewModal, WhatsNewModalHandle } from "../components/WhatsNewModal/WhatsNewModal";
import { WelcomeModal, WelcomeModalHandle } from "../components/WelcomeModal/WelcomeModal";
import {
	getNewerReleaseSlides,
	getReleaseSlidesForLastVersion,
	LAST_VERSION,
	ReleaseSlide,
} from "../releaseNotes/versions";

interface WhatsNewContextType {
	showWhatsNew: () => void;
	showWelcome: () => void;
}

const WhatsNewContext = createContext<WhatsNewContextType | undefined>(undefined);

export function useWhatsNew(): WhatsNewContextType {
	const context: WhatsNewContextType | undefined = useContext(WhatsNewContext);
	if (context === undefined) {
		throw new Error("useWhatsNew must be used within a WhatsNewProvider");
	}
	return context;
}

interface WhatsNewProviderProps {
	children: ReactNode;
}

export function WhatsNewProvider({ children }: WhatsNewProviderProps): JSX.Element {
	const whatsNewRef = useRef<WhatsNewModalHandle>(null);
	const welcomeRef = useRef<WelcomeModalHandle>(null);
	const { currentUser } = useAuth();
	const { startTour, completedTourIds } = useTour();
	const [slides, setSlides] = useState<ReleaseSlide[]>([]);

	const showWhatsNew = useCallback((): void => {
		const newSlides: ReleaseSlide[] = getReleaseSlidesForLastVersion();
		setSlides(newSlides);
		whatsNewRef.current?.show();
	}, []);

	const showWelcome = useCallback((): void => {
		welcomeRef.current?.show();
	}, []);

	// Show the appropriate modal automatically on login
	useEffect(() => {
		if (!currentUser) return;

		if (currentUser.app_version === null) {
			// New user — show the welcome carousel
			const timer = setTimeout((): void => {
				welcomeRef.current?.show();
			}, 500);
			return (): void => clearTimeout(timer);
		}

		if (currentUser.app_version !== LAST_VERSION) {
			// Returning user with outdated version — show what's new slides
			const newSlides: ReleaseSlide[] = getNewerReleaseSlides(currentUser.app_version);
			if (newSlides.length > 0) {
				setSlides(newSlides);
				const timer = setTimeout((): void => {
					whatsNewRef.current?.show();
				}, 500);
				return (): void => clearTimeout(timer);
			}
		}
	}, [currentUser]);

	return (
		<WhatsNewContext.Provider value={{ showWhatsNew, showWelcome }}>
			{children}
			<WhatsNewModal ref={whatsNewRef} slides={slides} />
			<WelcomeModal
				ref={welcomeRef}
				onFinish={(): void => {
					if (!completedTourIds.has("app-overview")) {
						startTour("app-overview");
					}
				}}
			/>
		</WhatsNewContext.Provider>
	);
}
