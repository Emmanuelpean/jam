import React, { forwardRef, JSX } from "react";
import { SlideCarouselModal, SlideCarouselModalHandle } from "../SlideCarouselModal/SlideCarouselModal";
import { LAST_VERSION, ReleaseSlide } from "../../releaseNotes/versions";
import packageJson from "../../../package.json";

export type WhatsNewModalHandle = SlideCarouselModalHandle;

interface WhatsNewModalProps {
	slides: ReleaseSlide[];
}

export const WhatsNewModal = forwardRef<WhatsNewModalHandle, WhatsNewModalProps>(
	({ slides }: WhatsNewModalProps, ref): JSX.Element => {
		return (
			<SlideCarouselModal
				ref={ref}
				id="whats-new-modal"
				title={`What's New in Version ${LAST_VERSION}`}
				titleIcon="bi-stars"
				slides={slides}
				finishText="Got it!"
				finishIcon="bi-check-lg"
			/>
		);
	}
);
