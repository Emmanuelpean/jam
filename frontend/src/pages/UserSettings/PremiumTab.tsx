import React, { JSX } from "react";
import { Badge, Card, Col, OverlayTrigger, Row, Tooltip } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { ActionButton } from "../../components/rendering/form/ActionButton";
import { CheckoutModal } from "./CheckoutModal";
import { DataContextValue, useDataContext } from "../../contexts/DataContext";
import { useGlobalToast } from "../../hooks/useNotificationToast";

interface PremiumTabProps {
	showCheckout: boolean;
	setShowCheckout: (show: boolean) => void;
}

export const PremiumTab: React.FC<PremiumTabProps> = ({
	showCheckout,
	setShowCheckout,
}: PremiumTabProps): JSX.Element => {
	const { currentUser } = useAuth();
	const dataContext: DataContextValue = useDataContext();
	const { showToastSuccess } = useGlobalToast();

	const handleRightClick = (e: any, email: string) => {
		e.preventDefault();
		navigator.clipboard.writeText(email).then((_: void): void => {
			showToastSuccess(`${email} to clipboard`);
		});
	};

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

	return (
		<>
			<Card className="mb-4 text-center">
				<Card.Body>
					<h2>{currentUser?.toast_active ? "Premium Active" : "Upgrade to Premium"}</h2>
					<p className="text-muted">
						{currentUser?.toast_active
							? "You have Premium"
							: "Unlock powerful features to supercharge your job search"}
					</p>

					{/* NEW SUMMARY SECTION */}
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
					{!currentUser?.toast_active && (
						<>
							<h3 className="mt-4">£5/month</h3>
							<p className="text-muted">Cancel anytime</p>
							<ActionButton
								onClick={() => setShowCheckout(true)}
								defaultIcon="bi-gem"
								defaultText="Subscribe Now"
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
							<div className="d-flex align-items-center mb-3">
								<i className="bi bi-envelope fs-1 me-3"></i>
								<h5 className="mb-0">Automatic Job Alert Email Scraping</h5>
							</div>
							<p>
								Automatically scrape and import jobs from job boards such as LinkedIn and Indeed by
								forwarding job alert emails to:
							</p>
							<p className="text-center">
								<strong>{dataContext.config.scraper_email}</strong>
							</p>
							<p>
								Simply set up email forwarding rules in your inbox, and new job opportunities will be
								automatically added to your dashboard.
							</p>
							<p className="mb-2">The following job boards are currently supported:</p>
							<div className="d-flex flex-wrap gap-2 mb-3">
								{jobBoards.map((board) => {
									const email = dataContext.config.platform_sender_emails?.[board.emailKey];

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
							<div className="d-flex align-items-center mb-3">
								<i className="bi bi-robot fs-1 me-3"></i>
								<h5 className="mb-0">AI Job Matching</h5>
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
				<CheckoutModal
					show={showCheckout}
					onHide={() => setShowCheckout(false)}
					userEmail={currentUser.email}
				/>
			)}
		</>
	);
};
