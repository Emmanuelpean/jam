import React, { createContext, useContext, useRef, useEffect, useState, useCallback, ReactNode, JSX } from "react";
import { useAuth } from "./AuthContext";
import { WhatsNewModalHandle, WhatsNewModal } from "../components/WhatsNewModal/WhatsNewModal";
import { WelcomeModalHandle, WelcomeModal } from "../components/WelcomeModal/WelcomeModal";
import { getNewerReleaseSlides, getReleaseSlidesForVersion, ReleaseSlide } from "../releaseNotes/versions";
import packageJson from "../../package.json";

interface WhatsNewContextType {
	showWhatsNew: () => void;
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
	const [slides, setSlides] = useState<ReleaseSlide[]>([]);

	const showWhatsNew = useCallback((): void => {
		const newSlides: ReleaseSlide[] = getReleaseSlidesForVersion(packageJson.version);
		setSlides(newSlides);
		whatsNewRef.current?.show();
	}, []);

	// Show the appropriate modal automatically on login
	useEffect(() => {
		console.log(currentUser);
		if (!currentUser) return;

		if (currentUser.app_version === null) {
			// New user — show the welcome carousel
			const timer = setTimeout((): void => {
				welcomeRef.current?.show();
			}, 500);
			return (): void => clearTimeout(timer);
		}

		if (currentUser.app_version !== packageJson.version) {
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
		<WhatsNewContext.Provider value={{ showWhatsNew }}>
			{children}
			<WhatsNewModal ref={whatsNewRef} slides={slides} />
			<WelcomeModal ref={welcomeRef} />
		</WhatsNewContext.Provider>
	);
}
