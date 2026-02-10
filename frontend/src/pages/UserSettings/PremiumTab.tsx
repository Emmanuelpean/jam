import React, { JSX, ReactNode, useEffect, useRef, useState } from "react";
import { Alert, Badge, Card, Col, OverlayTrigger, Row, Tooltip } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { useConfig } from "../../contexts/ConfigContext";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { useAlert } from "../../contexts/AlertContext";
import { ApiResponse } from "../../services/api/Base";
import { ActionToggle } from "../../components/rendering/form/ActionToggle";
import { paymentsApi, PortalSessionResponse } from "../../services/api/Payments";
import { ScrapingGuideModal, ScrapingGuideModalHandle } from "../../components/ScrapingGuideModal/ScrapingGuideModal";
import { forwardingConfirmationApi } from "../../services/api/Services";
import { ForwardingConfirmationLinkData } from "../../services/schemas/Services";
import { PremiumDetails } from "../../services/schemas/Core";

interface SubscriptionStatusDisplay {
	title: string;
	message: string | ReactNode;
	variant: "success" | "danger" | "warning" | "info";
	showSubscribeButton: boolean;
	badgeVariant: "success" | "danger" | "warning" | "info" | "primary";
	icon: string;
}

interface JobBoard {
	name: string;
	url: string;
	emailKey: string;
	icon: string;
}

const getSubscriptionStatusDisplay = (
	status: string | null,
	trialEndDate: number | null,
	supportEmail: string,
	premiumDetails: PremiumDetails | null
): SubscriptionStatusDisplay => {
	// Calculate trial days remaining from absolute timestamp (seconds since epoch)
	let trialDaysRemaining: number | null = null;
	if (trialEndDate !== null) {
		const nowSeconds: number = Date.now() / 1000;
		const remainingSeconds: number = trialEndDate - nowSeconds;
		trialDaysRemaining = Math.max(0, Math.ceil(remainingSeconds / (60 * 60 * 24)));
	}

	if (premiumDetails?.is_active && !status) {
		return {
			title: "Premium",
			message: "All features unlocked",
			variant: "success",
			badgeVariant: "success",
			showSubscribeButton: false,
			icon: "bi-gem",
		};
	}

	if (!status || status === "canceled") {
		return {
			title: "Free Plan",
			message: "Upgrade to unlock powerful automation features",
			variant: "info",
			badgeVariant: "info",
			showSubscribeButton: true,
			icon: "bi-star",
		};
	}
	if (status === "trialing" && trialDaysRemaining !== null && trialDaysRemaining > 0) {
		return {
			title: "Premium (Trial)",
			message: `${trialDaysRemaining} day${trialDaysRemaining !== 1 ? "s" : ""} remaining in your free trial`,
			variant: "success",
			badgeVariant: "success",
			showSubscribeButton: false,
			icon: "bi-gem",
		};
	}
	if (status === "active" || status == "trialing") {
		return {
			title: "Premium",
			message: "All features unlocked",
			variant: "success",
			badgeVariant: "success",
			showSubscribeButton: false,
			icon: "bi-gem",
		};
	}
	return {
		title: "Unknown Status",
		message: (
			<>
				Please contact <a href={`mailto:${supportEmail}`}>support</a> for assistance
			</>
		),
		variant: "warning",
		badgeVariant: "warning",
		showSubscribeButton: false,
		icon: "bi-question-circle",
	};
};

export const PremiumTab = (): JSX.Element => {
	const { currentUser, token, updateCurrentUser, fetchUserInfo } = useAuth();
	const { config } = useConfig();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const { showConfirm } = useAlert();
	const scrapingGuideRef = useRef<ScrapingGuideModalHandle>(null);
	const [stripeLoading, setStripeLoading] = useState<boolean>(false);
	const [jobRatingLoading, setJobRatingLoading] = useState<boolean>(false);
	const [jobScrapingLoading, setJobScrapingLoading] = useState<boolean>(false);
	const [confirmationLink, setConfirmationLink] = useState<ForwardingConfirmationLinkData | null>(null);

	// Poll user data every 5 seconds while tab is active
	useEffect(() => {
		if (!token) return;

		// Set up polling interval
		const intervalId = setInterval((): void => {
			void fetchUserInfo(token);
			console.log(currentUser);
		}, 5000);

		return (): void => {
			void clearInterval(intervalId);
		};
	}, [token, fetchUserInfo]);

	// Fetch pending forwarding confirmation links
	useEffect((): void => {
		if (!token) return;
		const fetchPending = async (): Promise<void> => {
			try {
				const response: ApiResponse<ForwardingConfirmationLinkData | null> =
					await forwardingConfirmationApi.getPending(token);
				setConfirmationLink(response.data ?? null);
			} catch {
				setConfirmationLink(null);
			}
		};
		void fetchPending();
	}, [token]);

	const promptMarkAsUsed = async (): Promise<void> => {
		if (!token || !confirmationLink) return;
		const confirmed: boolean = await showConfirm({
			title: "Mark as Used",
			message: `Mark this ${confirmationLink.platform} confirmation link as used?`,
			confirmText: "Yes, mark as used",
			cancelText: "No, keep it",
			id: "confirmation-link-prompt",
		});
		if (!confirmed) return;
		try {
			await forwardingConfirmationApi.markAsUsed(confirmationLink.id, token);
			setConfirmationLink(null);
			showToastSuccess("Confirmation link marked as used");
		} catch {
			showToastError("Failed to update confirmation link");
		}
	};

	const handleConfirmationLinkClick = (): void => {
		if (!confirmationLink) return;
		window.open(confirmationLink.url, "_blank");
		void promptMarkAsUsed();
	};

	const handleSubscribe = async (): Promise<void> => {
		if (!token) return;
		setStripeLoading(true);

		try {
			const response: ApiResponse<PortalSessionResponse> = await paymentsApi.createSubscriptionCheckout(token);
			if (response.data?.url) {
				// Set flag to trigger polling when user returns from Stripe
				sessionStorage.setItem("stripe_redirect", "true");
				window.location.href = response.data.url;
			} else {
				showToastError("Failed to create checkout session. Please try again.");
				setStripeLoading(false);
			}
		} catch (error) {
			console.log(error);
			showToastError("Failed to create checkout session. Please try again.");
			setStripeLoading(false);
		}
	};

	const handleManageSubscription = async (): Promise<void> => {
		if (!token) return;
		setStripeLoading(true);

		try {
			const response: ApiResponse<PortalSessionResponse> = await paymentsApi.createPortalSession(token);
			if (response.data?.url) {
				// Set flag to trigger polling when user returns from Stripe
				sessionStorage.setItem("stripe_redirect", "true");
				window.location.href = response.data.url;
			} else {
				showToastError("Failed to open subscription management. Please try again.");
				setStripeLoading(false);
			}
		} catch (error) {
			showToastError("Failed to open subscription management. Please try again.");
			setStripeLoading(false);
		}
	};

	const handleRightClick = (e: React.MouseEvent, email: string): void => {
		e.preventDefault();
		navigator.clipboard.writeText(email).then((_: void): void => {
			showToastSuccess(`${email} copied to clipboard`);
		});
	};

	const copyScraperEmail = (_: React.MouseEvent): void => {
		navigator.clipboard.writeText(config.support_email).then((_: void): void => {
			showToastSuccess(`${config.support_email} copied to clipboard`);
		});
	};

	const statusDisplay: SubscriptionStatusDisplay = getSubscriptionStatusDisplay(
		currentUser?.stripe_details.subscription_status ?? null,
		currentUser?.stripe_details.trial_end_date ?? null,
		config?.support_email,
		currentUser?.premium ?? null
	);
	const hasActiveSubscription: boolean = ["active", "trialing", "paused"].includes(
		currentUser?.stripe_details.subscription_status || ""
	);

	const jobBoards: JobBoard[] = [
		{ name: "LinkedIn", url: "https://linkedin.com", icon: "linkedin", emailKey: "linkedin" },
		{ name: "Indeed", url: "https://indeed.com", icon: "briefcase", emailKey: "indeed" },
		{ name: "VeganJobs", url: "https://veganjobs.com", icon: "flower1", emailKey: "veganjobs" },
		{ name: "NHS", url: "https://www.jobs.nhs.uk", icon: "hospital", emailKey: "nhs" },
	];

	const handleToggleJobRating = (): void => {
		setJobRatingLoading(true);
		updateCurrentUser({
			premium: { job_rating_active: !currentUser?.premium.job_rating_active },
		})
			.then((): void => {})
			.catch((): void => showToastError("Failed to update settings"))
			.finally((): void => setJobRatingLoading(false));
	};

	const handleToggleJobScraping = (): void => {
		setJobScrapingLoading(true);
		updateCurrentUser({
			premium: { job_scraping_active: !currentUser?.premium.job_scraping_active },
		})
			.then((): void => {})
			.catch((): void => showToastError("Failed to update settings"))
			.finally((): void => setJobScrapingLoading(false));
	};

	return (
		<>
			{/* Forwarding Confirmation Alert */}
			{confirmationLink && (
				<Alert
					id="confirmation-link-alert"
					variant="warning"
					className="mb-4"
					show
					dismissible
					onClose={() => void promptMarkAsUsed()}
				>
					<Alert.Heading style={{ fontSize: "0.95rem" }} id="confirmation-link-heading">
						<i className="bi bi-exclamation-triangle me-2" />
						{confirmationLink.platform} forwarding confirmation required
					</Alert.Heading>
					<p className="mb-2 small">
						Click the link below to confirm email forwarding for {confirmationLink.platform}:
					</p>
					<a
						href={confirmationLink.url}
						target="_blank"
						rel="noreferrer"
						className="small"
						id="confirmation-link-url"
						onClick={(e) => {
							e.preventDefault();
							handleConfirmationLinkClick();
						}}
					>
						Confirm forwarding
						<i className="bi bi-box-arrow-up-right ms-1" />
					</a>
				</Alert>
			)}

			{/* Hero Card */}
			<Card className="mb-4">
				<Card.Body className={"premium-card"}>
					{/* Subscription Status Section */}
					<div className="text-center mb-4">
						<div className="premium-status-icon mx-auto mb-3">
							<i className={statusDisplay.icon}></i>
						</div>
						<h3 className="mb-2" id="status-title">
							{statusDisplay.title}
						</h3>
						<p className="text-muted mb-4" style={{ fontSize: "1rem" }} id={"status-message"}>
							{statusDisplay.message}
						</p>

						{/* Action Buttons */}
						{statusDisplay.showSubscribeButton ? (
							<div className="d-flex flex-column align-items-center gap-3">
								<div className="premium-price-tag">
									<span style={{ fontSize: "1.5rem", fontWeight: 700 }}>£5</span>
									<span style={{ opacity: 0.8 }}>/month</span>
								</div>
								{!currentUser?.stripe_details.trial_end_date && (
									<p className="text-muted mb-0">14-day free trial • Cancel anytime</p>
								)}
								<ActionButton
									onClick={handleSubscribe}
									defaultIcon="bi-gem"
									id="subscription-button"
									defaultText={
										currentUser?.stripe_details.trial_end_date ? "Subscribe" : "Start Free Trial"
									}
									loading={stripeLoading}
									loadingText="Loading..."
								/>
							</div>
						) : hasActiveSubscription ? (
							<div className="d-flex flex-column align-items-center gap-3">
								<div className="premium-price-tag">
									<span style={{ fontSize: "1.25rem", fontWeight: 600 }}>£5</span>
									<span style={{ opacity: 0.8 }}>/month</span>
								</div>
								<ActionButton
									onClick={handleManageSubscription}
									defaultIcon="bi-gear"
									loading={stripeLoading}
									id="subscription-button"
									defaultText="Manage Subscription"
									loadingText="Loading..."
								/>
							</div>
						) : null}
					</div>

					{/* Premium Description */}
					<div className="premium-divider" />
					<div className="premium-why-section">
						<h4 className="mb-3">
							<i className="bi bi-lightbulb me-2"></i>Why Premium?
						</h4>
						<p className="mb-2">
							If you're actively job hunting, you likely receive dozens of job alert emails every day from
							platforms like LinkedIn, Indeed, and others. Manually reviewing each job is time-consuming
							and exhausting.
						</p>
						<p className="mb-0">
							<strong>JAM Premium</strong> eliminates this wasted time by automatically scraping jobs from
							your email alerts, intelligently rating them based on your qualifications, and presenting
							everything in a unified dashboard with AI-powered match scores.
						</p>
					</div>
				</Card.Body>
			</Card>

			{/* Features Section */}
			<div className="premium-features-title">
				<i className="bi bi-stars"></i>
				<h4 className="mb-0">Premium Features</h4>
			</div>

			<Row>
				{/* Email Scraping Feature */}
				<Col md={6} className="mb-3">
					<Card className="h-100 premium-feature-card">
						<Card.Body>
							<div className="premium-feature-header">
								<div className="d-flex align-items-center">
									<div className="premium-feature-icon-wrapper">
										<i className="bi bi-envelope-paper"></i>
									</div>
									<div className="premium-feature-title-section">
										<p className="premium-feature-title">Job Scraping</p>
									</div>
								</div>
								{currentUser?.premium.is_active && (
									<ActionToggle
										id="email-scraping-toggle"
										label=""
										checked={currentUser?.premium.job_scraping_active || false}
										onChange={() => handleToggleJobScraping()}
										loading={jobScrapingLoading}
									/>
								)}
							</div>

							<p>
								Automatically scrape and import jobs from job aggregator platforms (<i>e.g.</i> Linkedin
								and Indeed) job alert emails.
							</p>

							<h6 className="premium-feature-section-title">How It Works</h6>
							<p>
								<strong>Stage 1 - Email Scraping</strong>: When a job alert email is forwarded to the
								JAM inbox, the system parses it to extract key details such as job title, salary,
								location, and company, depending on what each job board provides.
							</p>
							<p className="mb-4">
								<strong>Stage 2 - Deep Scraping</strong>: JAM then visits the corresponding job board
								page to collect richer information like the full job description. This deeper scraping
								is limited to XX jobs per month per user. After this limit is reached, new job alert
								emails are still parsed, but their job pages are not scraped further.
							</p>
							<p>
								Each scraped job appears in your dashboard, where you can review, import, or remove it.
								The location and company fields are automatically suggested based on your existing
								entries. You can also apply scraping filters to refine the results. For example, you can
								exclude jobs posted by specific companies or filter by location, salary range, or
								keywords.
							</p>

							<h6 className="premium-feature-section-title">Supported job boards:</h6>
							<div className="job-board-badges">
								{jobBoards.map((board) => {
									const email = config?.platform_sender_emails?.[board.emailKey];
									return (
										<OverlayTrigger
											key={board.name}
											placement="top"
											overlay={
												<Tooltip>
													<div>Forward emails from:</div>
													<div style={{ whiteSpace: "nowrap" }}>{email}</div>
													<div style={{ fontSize: "0.85em", opacity: 0.8 }}>
														(Right-click to copy)
													</div>
												</Tooltip>
											}
										>
											<Badge
												as="a"
												href={board.url}
												target="_blank"
												rel="noreferrer"
												className="text-decoration-none"
												onContextMenu={(e): void => handleRightClick(e, email)}
												style={{ cursor: "context-menu" }}
											>
												<i className={`bi bi-${board.icon} me-1`}></i>
												{board.name}
											</Badge>
										</OverlayTrigger>
									);
								})}
							</div>

							<p className="small text-muted">
								Need another job board?{" "}
								<a href={`mailto:${config?.support_email}?subject=Job Board Integration Request`}>
									Contact support
								</a>
							</p>

							<ActionButton
								onClick={() => scrapingGuideRef.current?.show()}
								defaultIcon="bi-book"
								defaultText="Setup Guide"
								variant="outline-primary"
								size="sm"
								className="mb-3"
							/>
						</Card.Body>
					</Card>
				</Col>

				{/* AI Matching Feature */}
				<Col md={6} className="mb-3">
					<Card className="h-100 premium-feature-card">
						<Card.Body>
							<div className="premium-feature-header">
								<div className="d-flex align-items-center">
									<div className="premium-feature-icon-wrapper">
										<i className="bi bi-robot"></i>
									</div>
									<div className="premium-feature-title-section">
										<p className="premium-feature-title">AI Job Matching</p>
									</div>
								</div>
								{currentUser?.premium.is_active && (
									<ActionToggle
										id="ai-matching-toggle"
										label=""
										checked={currentUser?.premium.job_rating_active}
										onChange={() => handleToggleJobRating()}
										loading={jobRatingLoading}
									/>
								)}
							</div>

							<p>
								Our AI analyses every job opportunity against your qualifications, delivering
								personalised match scores so you can focus on roles that truly matter.
							</p>

							<h6 className="premium-feature-section-title">How It Works</h6>
							<p className="small">
								When jobs are collected, AI automatically evaluates each one against your experience,
								education, skills, and interests - no manual work required.
							</p>

							<h6 className="premium-feature-section-title">Scoring Dimensions</h6>
							<ul className="scoring-dimensions">
								<li>
									<span>
										<strong>Overall Match</strong> — Holistic assessment of profile fit
									</span>
								</li>
								<li>
									<span>
										<strong>Technical Fit</strong> — Skills and methodology alignment
									</span>
								</li>
								<li>
									<span>
										<strong>Experience</strong> — Background and career level match
									</span>
								</li>
								<li>
									<span>
										<strong>Education</strong> — Academic credential compatibility
									</span>
								</li>
								<li>
									<span>
										<strong>Interest</strong> — Career goals and passion alignment
									</span>
								</li>
							</ul>
						</Card.Body>
					</Card>
				</Col>
			</Row>

			<ScrapingGuideModal ref={scrapingGuideRef} />
		</>
	);
};
