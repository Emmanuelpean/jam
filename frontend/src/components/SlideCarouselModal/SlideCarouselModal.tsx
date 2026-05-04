import React, { forwardRef, JSX, useCallback, useImperativeHandle, useRef, useState } from "react";
import { useArrowKeyNavigation } from "../../hooks/useArrowKeyNavigation";
import { Modal } from "react-bootstrap";
import JamModal from "../JamModal/JamModal";
import { ActionButton } from "../rendering/form/ActionButton";
import { useAuth } from "../../contexts/AuthContext";
import packageJson from "../../../package.json";
import { ReleaseSlide } from "../../releaseNotes/versions";
import "./SlideCarouselModal.scss";

export interface SlideCarouselModalHandle {
	show: () => void;
	hide: () => void;
}

interface SlideCarouselModalProps {
	id: string;
	title: string;
	titleIcon: string;
	slides: ReleaseSlide[];
	finishText: string;
	finishIcon: string;
	onFinish?: () => void;
}

export const SlideCarouselModal = forwardRef<SlideCarouselModalHandle, SlideCarouselModalProps>(
	({ id, title, titleIcon, slides, finishText, finishIcon, onFinish }: SlideCarouselModalProps, ref): JSX.Element => {
		const [show, setShow] = useState<boolean>(false);
		const [currentStep, setCurrentStep] = useState<number>(0);
		const [direction, setDirection] = useState<"next" | "prev" | null>(null);
		const [loading, setLoading] = useState<boolean>(false);
		const { updateCurrentUser } = useAuth();
		const [slideHeight, setSlideHeight] = useState<number | undefined>(undefined);
		const measureRef = useRef<HTMLDivElement | null>(null);

		const measureSlides = useCallback((): void => {
			if (!measureRef.current) return;
			const children = measureRef.current.children;
			let maxHeight = 0;
			for (let i = 0; i < children.length; i++) {
				maxHeight = Math.max(maxHeight, (children[i] as HTMLElement).offsetHeight);
			}
			if (maxHeight > 0) setSlideHeight(maxHeight);
		}, []);

		const isLastStep: boolean = currentStep === slides.length - 1;
		const isFirstStep: boolean = currentStep === 0;
		const slide: ReleaseSlide | undefined = slides[currentStep];

		useImperativeHandle(ref, () => ({
			show: (): void => {
				setCurrentStep(0);
				setDirection(null);
				setShow(true);
			},
			hide: (): void => setShow(false),
		}));

		const markAsSeen = async (): Promise<void> => {
			setLoading(true);
			try {
				await updateCurrentUser({ app_version: packageJson.version });
			} catch (error) {
				console.log("Error updating app version:", error);
			} finally {
				setLoading(false);
			}
			setShow(false);
			onFinish?.();
		};

		const handleNext = (): void => {
			if (isLastStep) {
				void markAsSeen();
			} else {
				setDirection("next");
				setCurrentStep((prev: number): number => prev + 1);
			}
		};

		const handleBack = (): void => {
			setDirection("prev");
			setCurrentStep((prev: number): number => prev - 1);
		};

		useArrowKeyNavigation({ active: show, onNext: handleNext, onPrev: handleBack, canGoPrev: !isFirstStep, nextOnEnter: true });

		if (!slide) return <></>;

		return (
			<JamModal
				show={show}
				onHide={markAsSeen}
				centered
				size="lg"
				className="slide-carousel-modal"
				id={id}
				onEntered={measureSlides}
			>
				<JamModal.Header onClose={markAsSeen}>
					<Modal.Title>
						<i className={`bi bi-${titleIcon} me-2`} />
						{title}
					</Modal.Title>
				</JamModal.Header>
				<Modal.Body>
					{/* Hidden container to measure all slides */}
					<div ref={measureRef} className="carousel-measure-container">
						{slides.map((s: ReleaseSlide, i: number) => (
							<div key={i} className="carousel-step">
								{s.version && <p className="carousel-step-version">V{s.version}</p>}
								{s.image ? (
									<img src={s.image} alt={s.title} className="carousel-step-image" />
								) : (
									<div className="carousel-step-icon">
										<i className={`bi bi-${s.icon}`} />
									</div>
								)}
								<h4 className="carousel-step-title">{s.title}</h4>
								<p className="carousel-step-description">{s.description}</p>
							</div>
						))}
					</div>
					<div
						key={currentStep}
						className={`carousel-step${direction ? ` slide-${direction}` : ""}`}
						style={slideHeight ? { minHeight: slideHeight } : undefined}
					>
						{slide.version && <p className="carousel-step-version">V{slide.version}</p>}
						{slide.image ? (
							<img src={slide.image} alt={slide.title} className="carousel-step-image" />
						) : (
							<div className="carousel-step-icon">
								<i className={`bi bi-${slide.icon}`} />
							</div>
						)}
						<h4 className="carousel-step-title">{slide.title}</h4>
						<p className="carousel-step-description">{slide.description}</p>
					</div>
					<div className="carousel-dots">
						{slides.map(
							(_: ReleaseSlide, index: number): JSX.Element => (
								<button
									key={index}
									className={`carousel-dot ${index === currentStep ? "active" : ""}`}
									onClick={() => {
										setDirection(index > currentStep ? "next" : "prev");
										setCurrentStep(index);
									}}
									aria-label={`Go to slide ${index + 1}`}
								/>
							)
						)}
					</div>
				</Modal.Body>
				<Modal.Footer>
					<div className="modal-buttons-container">
						{!isFirstStep && (
							<ActionButton
								id={`${id}-back-button`}
								variant="secondary"
								onClick={handleBack}
								defaultText="Back"
								defaultIcon="bi-arrow-left"
							/>
						)}
						<ActionButton
							id={`${id}-next-button`}
							variant="primary"
							onClick={handleNext}
							defaultText={isLastStep ? finishText : "Next"}
							defaultIcon={isLastStep ? finishIcon : "bi-arrow-right"}
							loading={loading}
							disabled={loading}
						/>
					</div>
				</Modal.Footer>
			</JamModal>
		);
	}
);
