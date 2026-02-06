import React, { forwardRef, JSX } from "react";
import { SlideCarouselModal, SlideCarouselModalHandle } from "../SlideCarouselModal/SlideCarouselModal";
import { ReleaseSlide, WELCOME_SLIDES } from "../../releaseNotes/versions";
import followupGif from "../../assets/demo_gifs/followup_email_demo.gif";

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
