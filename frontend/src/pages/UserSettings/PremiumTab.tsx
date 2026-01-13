import React, { JSX, useEffect, useState } from "react";
import { Alert, Badge, Card, Col, OverlayTrigger, Row, Tooltip } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { StripeCheckoutModal } from "./StripeCheckoutModal";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { ApiResponse } from "../../services/api/Base";
import { ActionToggle } from "../../components/rendering/form/ActionToggle";
import { paymentsApi, SubscriptionStatus } from "../../services/api/Payments";

interface PremiumTabProps {
	showCheckout: boolean;
	setShowCheckout: (show: boolean) => void;
}

export const PremiumTab: React.FC<PremiumTabProps> = ({
	showCheckout,
	setShowCheckout,
}: PremiumTabProps): JSX.Element => {
	const { currentUser, token, updateCurrentUser } = useAuth();
	const dataContext: DataContextValue = useDataContext();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const [loading, setLoading] = useState<boolean>(false);
	const [subscriptionChanged, setSubscriptionChanged] = useState<boolean>(false);
	const [jobRatingLoading, setJobRatingLoading] = useState<boolean>(false);
	const [jobScrapingLoading, setJobScrapingLoading] = useState<boolean>(false);
	const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatus>({
		status: null,
		trial_end: null,
	});

	useEffect((): void => {
		if (currentUser?.stripe_details.subscription_id) {
			fetchSubscriptionStatus().then((_) => {});
		}
	}, [currentUser?.stripe_details.subscription_id]);

	const fetchSubscriptionStatus = async (): Promise<void> => {
		if (!currentUser?.stripe_details.subscription_id || !token) return;

		try {
			const response: ApiResponse<SubscriptionStatus> = await paymentsApi.getSubscriptionStatus(
				currentUser.stripe_details.subscription_id,
				token,
			);
			setSubscriptionStatus(response.data);
		} catch (error) {
			console.error("Failed to fetch subscription status:", error);
		}
	};

	const getSubscriptionStatusDisplay = () => {
		const { status, trial_end } = subscriptionStatus;

		if (!status) {
			return {
				title: "Upgrade to Premium",
				message: "Unlock powerful features to supercharge your job search",
				variant: "info",
				showSubscribeButton: true,
			};
		} else if (trial_end) {
			const trial_days_remaining: number = Math.ceil(
				(new Date(trial_end).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24),
			);
			return {
				title: "Premium Active (Trial)",
				message:
					trial_days_remaining > 0
						? `${trial_days_remaining} day${trial_days_remaining !== 1 ? "s" : ""} of trial remaining`
						: "Trial ending soon",
				variant: "success",
				showSubscribeButton: false,
			};
		} else if (status === "active") {
			return {
				title: "Premium Active",
				message: "You have Premium (lucky you!)",
				variant: "success",
				showSubscribeButton: false,
			};
		} else {
			return {
				title: "Unknown Subscription Status",
				message: "Please contact support for assistance",
				variant: "warning",
				showSubscribeButton: false,
			};
		}
	};

	const handleRightClick = (e: React.MouseEvent, email: string) => {
		e.preventDefault();
		navigator.clipboard.writeText(email).then((_: void): void => {
			showToastSuccess(`${email} copied to clipboard`);
		});
	};

	const handleManageSubscription = async (): Promise<void> => {
		if (!currentUser?.email) return;

		try {
			setLoading(true);
			const response = await paymentsApi.createPortalSession(currentUser.email);
			window.location.href = response.data.url;
		} catch (error) {
			console.error("Portal session error:", error);
			showToastError(
				`Failed to access subscription portal. Please try again later or contact support at ${dataContext.config.support_email}`,
			);
			setLoading(false);
		}
	};

	const statusDisplay = getSubscriptionStatusDisplay();
	const hasActiveSubscription = ["active", "trialing", "past_due", "paused"].includes(
		subscriptionStatus.status || "",
	);

	const jobBoards = [
		{
			name: "LinkedIn",
			url: "https://linkedin.com",
			icon: "linkedin",
			emailKey: "linkedin",
		},
		{
			name: "Indeed",
			url: "https://indeed.com",
			icon: "briefcase",
			emailKey: "indeed",
		},
		{
			name: "VeganJobs",
			url: "https://veganjobs.com",
			icon: "flower1",
			emailKey: "veganjobs",
		},
		{
			name: "NHS",
			url: "https://www.jobs.nhs.uk",
			icon: "hospital",
			emailKey: "nhs",
		},
	];

	const handleToggleJobRating = () => {
		setJobRatingLoading(true);
		updateCurrentUser({ premium: { job_rating_active: !currentUser?.premium.job_rating_active } })
			.then(() => {
				showToastSuccess("Settings updated");
			})
			.catch(() => {
				showToastError("Failed to update settings");
			})
			.finally(() => {
				setJobRatingLoading(false);
			});
	};

	const handleToggleJobScraping = () => {
		setJobScrapingLoading(true);
		updateCurrentUser({ premium: { job_scraping_active: !currentUser?.premium.job_scraping_active } })
			.then(() => {
				showToastSuccess("Settings updated");
			})
			.catch(() => {
				showToastError("Failed to update settings");
			})
			.finally(() => {
				setJobScrapingLoading(false);
			});
	};

	return (
		<>
			<Card className="mb-4 text-center">
				<Card.Body>
					<h2>{statusDisplay.title}</h2>
					<Alert variant={statusDisplay.variant} className="d-inline-block mt-2">
						{statusDisplay.message}
					</Alert>
					<div className="text-start mt-4 mb-4" style={{ maxWidth: "900px", margin: "0 auto" }}>
						<h4 className="mb-3">Why Premium?</h4>
						<p>
							If you're actively job hunting, you likely receive dozens of job alert emails every day from
							platforms like LinkedIn, Indeed, and others. Manually reviewing each job is time-consuming
							and exhausting, you have to open every email, click through to job listings, and evaluate
							whether each role matches your qualifications.
						</p>
						<p>
							<strong>JAM Premium (TOAST)</strong> eliminates this wasted time by automatically scraping
							jobs from your email alerts, intelligently rating them based on your qualifications, and
							presenting everything in a unified dashboard. Instead of sifting through dozens of emails
							and job boards, you get a single, organised view with AI-powered match scores highlighting
							the opportunities that matter most.
						</p>
					</div>
					{statusDisplay.showSubscribeButton && (
						<>
							<h3 className="mt-4">£5/month</h3>
							<p className="text-muted">14-day free trial • Cancel anytime</p>
							<ActionButton
								onClick={() => setShowCheckout(true)}
								defaultIcon="bi-gem"
								id={"subscribe-button"}
								defaultText="Start Free Trial"
							/>
						</>
					)}
					{hasActiveSubscription && (
						<>
							<h3 className="mt-4">£5/month</h3>
							<p className="text-muted">Cancel anytime</p>
							<ActionButton
								onClick={handleManageSubscription}
								variant={"secondary"}
								defaultIcon="bi-gear"
								loading={loading}
								id={"manage-subscription-button"}
								defaultText="Manage Subscription"
							/>
						</>
					)}
				</Card.Body>
			</Card>

			<h4 className="mb-3">Premium Features</h4>

			<Row>
				<Col md={6} className="mb-3">
					<Card className="h-100">
						<Card.Body>
							<div className="d-flex align-items-center justify-content-between mb-3">
								<div className="d-flex align-items-center">
									<i className="bi bi-envelope fs-1 me-3"></i>
									<h5 className="mb-0">Automatic Job Alert Email Scraping</h5>
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
								Automatically scrape and import jobs from job boards such as LinkedIn and Indeed by
								forwarding job alert emails to:
							</p>
							<p className="text-center">
								<strong>{dataContext.config?.scraper_email}</strong>
							</p>
							<p>
								Simply set up email forwarding rules in your inbox, and new job opportunities will be
								automatically added to your dashboard.
							</p>
							<p className="mb-2">The following job boards are currently supported:</p>
							<div className="d-flex flex-wrap gap-2 mb-3">
								{jobBoards.map((board) => {
									const email = dataContext.config?.platform_sender_emails?.[board.emailKey];

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
							You can also request support for additional job boards by contacting{" "}
							<a
								href={`mailto:${dataContext.config?.support_email}?subject=Job Board Integration Request`}
							>
								support
							</a>
							.<h4 style={{ paddingTop: "1.5rem" }}>How It Works</h4>
							<p>
								Job scraping happens in two <strong>stages</strong>.
							</p>
							<p>
								<strong>Stage 1 – Email processing:</strong>
								<br /> When a job alert email is forwarded to the JAM inbox, the system parses it to
								extract key details such as job title, salary, location, and company, depending on what
								each job board provides.
							</p>
							<p>
								<strong>Stage 2 – Deep scraping:</strong>
								<br /> JAM then visits the corresponding job board page to collect richer information
								like the full job description. This deeper scraping is limited to XX jobs per month per
								user. After this limit is reached, new job alert emails are still parsed, but their job
								pages are not scraped further.
							</p>
							<h4 style={{ paddingTop: "1rem" }}>Managing scraped jobs</h4>
							<p>
								Each scraped job appears in your dashboard, where you can review, import, or remove it.
								The location and company fields are automatically suggested based on your existing
								entries to maintain consistency. If you receive too many job alerts, you can use
								scraping filters to control which jobs are captured—for example, you can add a filter to
								exclude jobs posted by specific companies or filter by location, salary range, or
								keywords.
							</p>
						</Card.Body>
					</Card>
				</Col>

				<Col md={6} className="mb-3">
					<Card className="h-100">
						<Card.Body>
							<div className="d-flex align-items-center justify-content-between mb-3">
								<div className="d-flex align-items-center">
									<i className="bi bi-robot fs-1 me-3"></i>
									<h5 className="mb-0">AI Job Matching</h5>
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
								Transform your job search with intelligent automation. Our advanced AI system
								continuously analyses every job opportunity against your unique qualifications,
								delivering personalized match scores so you can focus on the roles that truly matter.
							</p>

							<h4>How It Works</h4>
							<p>
								When new jobs are collected from your connected job boards, our AI automatically
								evaluates each one against your qualifications. The system considers your professional
								experience, education, technical skills, and career interests to provide comprehensive
								match scores—no manual work required.
							</p>

							<h4>Comprehensive Scoring Across 5 Key Dimensions</h4>
							<ul>
								<li>
									<strong>Overall Match Score</strong> - Holistic assessment combining all factors to
									determine how well the position fits your complete profile
								</li>
								<li>
									<strong>Technical Fit</strong> - How your skills, tools, and methodologies align
									with requirements
								</li>
								<li>
									<strong>Experience Alignment</strong> - Whether your background and career level
									match expectations
								</li>
								<li>
									<strong>Educational Match</strong> - How your academic credentials fit the position
								</li>
								<li>
									<strong>Interest Score</strong> - Whether the role aligns with your career goals and
									passions
								</li>
							</ul>
						</Card.Body>
					</Card>
				</Col>
			</Row>

			{currentUser?.email && (
				<StripeCheckoutModal
					show={showCheckout}
					onHide={() => setShowCheckout(false)}
					userEmail={currentUser.email}
				/>
			)}
		</>
	);
};
