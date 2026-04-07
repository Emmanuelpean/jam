import React, { forwardRef, JSX } from "react";
import { SlideCarouselModal, SlideCarouselModalHandle } from "../SlideCarouselModal/SlideCarouselModal";
import { WELCOME_SLIDES } from "../../releaseNotes/versions";

export type WelcomeModalHandle = SlideCarouselModalHandle;

interface WelcomeModalProps {
	onFinish?: () => void;
}

export const WelcomeModal = forwardRef<WelcomeModalHandle, WelcomeModalProps>(({ onFinish }, ref): JSX.Element => {
	return (
		<SlideCarouselModal
			ref={ref}
			id="welcome-modal"
			title="Welcome to Jam"
			titleIcon="stars"
			slides={WELCOME_SLIDES}
			finishText="Get Started!"
			finishIcon="bi-rocket-takeoff"
			onFinish={onFinish}
		/>
	);
});
