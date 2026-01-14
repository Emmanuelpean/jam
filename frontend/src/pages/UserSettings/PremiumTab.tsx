import React, { JSX, useEffect, useState } from "react";
import { Badge, Card, Col, OverlayTrigger, Row, Tooltip } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import { ApiResponse } from "../../services/api/Base";
import { ActionToggle } from "../../components/rendering/form/ActionToggle";
import { paymentsApi, PortalSessionResponse, SubscriptionStatus } from "../../services/api/Payments";
import LoadingSpinner from "../../components/spinner/Spinner";

const defaultSubscriptionStatus = {
	status: "unknowm",
	trial_end: null,
};

interface SubscriptionStatusDisplay {
	title: string;
	message: string;
	variant: "success" | "danger" | "warning" | "info";
	showSubscribeButton: boolean;
	badgeVariant: "success" | "danger" | "warning" | "info" | "primary";
	icon: string;
}

const getSubscriptionStatusDisplay = (status: string | null, trialEnd: number | null): SubscriptionStatusDisplay => {
	if (!status) {
		return {
			title: "Free Plan",
			message: "Upgrade to unlock powerful automation features",
			variant: "info",
			badgeVariant: "info",
			showSubscribeButton: true,
			icon: "bi-star",
		};
	} else if (trialEnd) {
		const remainingDays = Math.ceil((trialEnd - Date.now() / 1000) / 86400);
		return {
			title: "Premium (Trial)",
			message: `${remainingDays} day${remainingDays !== 1 ? "s" : ""} remaining in your free trial`,
			variant: "success",
			badgeVariant: "success",
			showSubscribeButton: false,
			icon: "bi-gem",
		};
	} else if (status === "active") {
		return {
			title: "Premium",
			message: "All features unlocked",
			variant: "success",
			badgeVariant: "success",
			showSubscribeButton: false,
			icon: "bi-gem",
		};
	} else {
		return {
			title: "Unknown Status",
			message: "Please contact support for assistance",
			variant: "warning",
			badgeVariant: "warning",
			showSubscribeButton: false,
			icon: "bi-question-circle",
		};
	}
};

export const PremiumTab = (): JSX.Element => {
	const { currentUser, token, updateCurrentUser, fetchUserInfo } = useAuth();
	const dataContext: DataContextValue = useDataContext();
	const { showToastSuccess, showToastError } = useGlobalToast();
	const [stripeLoading, setStripeLoading] = useState<boolean>(false);
	const [subscriptionLoading, setSubscriptionLoading] = useState<boolean>(false);
	const [jobRatingLoading, setJobRatingLoading] = useState<boolean>(false);
	const [jobScrapingLoading, setJobScrapingLoading] = useState<boolean>(false);
	const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatus>(defaultSubscriptionStatus);

	const fetchSubscriptionStatus = async (): Promise<void> => {
		if (!token) return;
		try {
			setSubscriptionLoading(true);
			const response: ApiResponse<SubscriptionStatus> = await paymentsApi.getSubscriptionStatus(token);
			setSubscriptionStatus(response.data);
		} catch (error) {
			setSubscriptionStatus({ status: "error", trial_end: null });
		} finally {
			setSubscriptionLoading(false);
		}
	};

	useEffect((): void => {
		fetchSubscriptionStatus().finally(() => {});
	}, [currentUser?.stripe_details.subscription_id]);

	useEffect(() => {
		const params = new URLSearchParams(window.location.search);
		const url = new URL(window.location.href);
		console.log(window.location.href);

		if (params.get("success") === "true") {
			console.log("here");
			// Set up polling to check subscription status
			let pollCount = 0;
			const maxPolls = 100; // Poll up to 10 times
			const pollingInterval = 3000; // Poll every 3 seconds

			const intervalId = setInterval(() => {
				console.log("Polling for subscription status...");
				pollCount++;

				if (pollCount >= maxPolls) {
					clearInterval(intervalId);
					return;
				}

				// Poll user data and subscription status
				if (token) {
					fetchUserInfo(token).then(() => {
						paymentsApi.getSubscriptionStatus(token).then(() => {});
					});
				}
			}, pollingInterval);

			window.history.replaceState({}, document.title, url.pathname);

			return () => {
				clearInterval(intervalId);
			};
		}
	}, [token]);

	const handleSubscribe = async () => {
		if (!token) return;
		setStripeLoading(true);

		try {
			const response: ApiResponse<PortalSessionResponse> = await paymentsApi.createSubscriptionCheckout(token);
			if (response.data?.url) {
				window.location.href = response.data.url;
			} else {
				showToastError("Failed to create checkout session. Please try again.");
			}
		} catch (error) {
			showToastError("Failed to create checkout session. Please try again.");
		} finally {
			setStripeLoading(false);
		}
	};

	const handleManageSubscription = async () => {
		if (!token) return;
		setStripeLoading(true);

		try {
			const response = await paymentsApi.createPortalSession(token);
			if (response.data?.url) {
				window.location.href = response.data.url;
			} else {
				showToastError("Failed to open subscription management. Please try again.");
			}
		} catch (error) {
			showToastError("Failed to open subscription management. Please try again.");
		} finally {
			setStripeLoading(false);
		}
	};

	const handleRightClick = (e: React.MouseEvent, email: string) => {
		e.preventDefault();
		navigator.clipboard.writeText(email).then((_: void): void => {
			showToastSuccess(`${email} copied to clipboard`);
		});
	};

	const statusDisplay: SubscriptionStatusDisplay = getSubscriptionStatusDisplay(
		subscriptionStatus.status,
		subscriptionStatus.trial_end,
	);
	const hasActiveSubscription = ["active", "trialing", "paused"].includes(subscriptionStatus.status || "");

	const jobBoards = [
		{ name: "LinkedIn", url: "https://linkedin.com", icon: "linkedin", emailKey: "linkedin" },
		{ name: "Indeed", url: "https://indeed.com", icon: "briefcase", emailKey: "indeed" },
		{ name: "VeganJobs", url: "https://veganjobs.com", icon: "flower1", emailKey: "veganjobs" },
		{ name: "NHS", url: "https://www.jobs.nhs.uk", icon: "hospital", emailKey: "nhs" },
	];

	const handleToggleJobRating = () => {
		setJobRatingLoading(true);
		updateCurrentUser({ premium: { job_rating_active: !currentUser?.premium.job_rating_active } })
			.then(() => {})
			.catch(() => showToastError("Failed to update settings"))
			.finally(() => setJobRatingLoading(false));
	};

	const handleToggleJobScraping = () => {
		setJobScrapingLoading(true);
		updateCurrentUser({ premium: { job_scraping_active: !currentUser?.premium.job_scraping_active } })
			.then(() => {})
			.catch(() => showToastError("Failed to update settings"))
			.finally(() => setJobScrapingLoading(false));
	};

	return (
		<>
			<Card className="mb-4">
				<Card.Body>
					{subscriptionLoading ? (
						<div className="py-5">
							<LoadingSpinner text={"Loading subscription status..."} />
						</div>
					) : (
						<>
							{/* Subscription Status Section */}
							<div className="text-center mb-4">
								<div className="d-flex align-items-center justify-content-center gap-3 mb-3">
									<i className={`${statusDisplay.icon} fs-1`}></i>
									<div className="text-start">
										<h3 className="mb-1" id={"status-title"}>
											{statusDisplay.title}
										</h3>
										<p className="text-muted mb-0" style={{ fontSize: "0.95rem" }}>
											{statusDisplay.message}
										</p>
									</div>
								</div>

								{/* Action Buttons */}
								<div className="d-flex flex-column align-items-center gap-2">
									{statusDisplay.showSubscribeButton ? (
										<>
											<div className="mb-2">
												<h4 className="mb-1">£5/month</h4>
												<p className="text-muted mb-0">14-day free trial • Cancel anytime</p>
											</div>
											<ActionButton
												onClick={handleSubscribe}
												defaultIcon="bi-gem"
												id={"subscribe-button"}
												defaultText="Start Free Trial"
												loading={stripeLoading}
												loadingText="Loading..."
											/>
										</>
									) : hasActiveSubscription ? (
										<>
											<div className="mb-2">
												<h5 className="mb-1">£5/month</h5>
												<p className="text-muted mb-0 small">Cancel anytime</p>
											</div>
											<ActionButton
												onClick={handleManageSubscription}
												variant={"secondary"}
												defaultIcon="bi-gear"
												loading={stripeLoading}
												id={"manage-subscription-button"}
												defaultText="Manage Subscription"
												loadingText={"Loading..."}
											/>
										</>
									) : null}
								</div>
							</div>

							{/* Premium Description - Now Below Status */}
							<div
								className="text-start mt-4 pt-4"
								style={{
									maxWidth: "900px",
									margin: "0 auto",
									borderTop: "1px solid rgba(0,0,0,0.1)",
								}}
							>
								<h4 className="mb-3">Why Premium?</h4>
								<p>
									If you're actively job hunting, you likely receive dozens of job alert emails every
									day from platforms like LinkedIn, Indeed, and others. Manually reviewing each job is
									time-consuming and exhausting, you have to open every email, click through to job
									listings, and evaluate whether each role matches your qualifications.
								</p>
								<p>
									<strong>JAM Premium (TOAST)</strong> eliminates this wasted time by automatically
									scraping jobs from your email alerts, intelligently rating them based on your
									qualifications, and presenting everything in a unified dashboard. Instead of sifting
									through dozens of emails and job boards, you get a single, organised view with
									AI-powered match scores highlighting the opportunities that matter most.
								</p>
							</div>
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
		</>
	);
};
