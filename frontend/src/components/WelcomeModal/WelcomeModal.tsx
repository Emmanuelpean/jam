import React, { forwardRef, JSX } from "react";
import { SlideCarouselModal, SlideCarouselModalHandle } from "../SlideCarouselModal/SlideCarouselModal";
import { WELCOME_SLIDES } from "../../releaseNotes/versions";

export type WelcomeModalHandle = SlideCarouselModalHandle;

export const WelcomeModal = forwardRef<WelcomeModalHandle>((_props, ref): JSX.Element => {
	return (
		<SlideCarouselModal
			ref={ref}
			id="welcome-modal"
			title="Welcome to Jam"
			titleIcon="bi-hand-thumbs-up"
			slides={WELCOME_SLIDES}
			finishText="Get Started!"
			finishIcon="bi-rocket-takeoff"
		/>
	);
});
