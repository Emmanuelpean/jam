import React, { JSX, ReactNode, useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "./AuthContext";
import { useTour } from "./TourContext";
import { WhatsNewModal, WhatsNewModalHandle } from "../components/WhatsNewModal/WhatsNewModal";
import { WelcomeModal, WelcomeModalHandle } from "../components/WelcomeModal/WelcomeModal";
import { TourHintPopup } from "../components/TourHintPopup/TourHintPopup";
import {
	getNewerReleaseSlides,
	getReleaseSlidesForLastVersion,
	LAST_VERSION,
	ReleaseSlide,
} from "../releaseNotes/versions";
import { WhatsNewContext } from "./WhatsNewContext.context";

export { useWhatsNew } from "./WhatsNewContext.context";
export type { WhatsNewContextType } from "./WhatsNewContext.context";

interface WhatsNewProviderProps {
	children: ReactNode;
}

export function WhatsNewProvider({ children }: WhatsNewProviderProps): JSX.Element {
	const whatsNewRef = useRef<WhatsNewModalHandle>(null);
	const welcomeRef = useRef<WelcomeModalHandle>(null);
	const { currentUser } = useAuth();
	const { isTourSelectOpen } = useTour();
	const [slides, setSlides] = useState<ReleaseSlide[]>([]);
	const [showTourHint, setShowTourHint] = useState<boolean>(false);
	const suppressTourHintRef = useRef<boolean>(false);

	useEffect(() => {
		if (isTourSelectOpen) setShowTourHint(false);
	}, [isTourSelectOpen]);

	const showWhatsNew = useCallback((): void => {
		const newSlides: ReleaseSlide[] = getReleaseSlidesForLastVersion();
		setSlides(newSlides);
		whatsNewRef.current?.show();
	}, []);

	const showWelcome = useCallback((): void => {
		suppressTourHintRef.current = true;
		welcomeRef.current?.show({ updateVersion: false });
	}, []);

	// Show the appropriate modal automatically on login
	useEffect(() => {
		if (!currentUser) return;

		if (currentUser.app_version === null) {
			// New user — show the welcome carousel
			const timer = setTimeout((): void => {
				suppressTourHintRef.current = false;
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
					if (suppressTourHintRef.current) {
						suppressTourHintRef.current = false;
						return;
					}
					setShowTourHint(true);
				}}
			/>
			{showTourHint && <TourHintPopup onClose={(): void => setShowTourHint(false)} />}
		</WhatsNewContext.Provider>
	);
}
