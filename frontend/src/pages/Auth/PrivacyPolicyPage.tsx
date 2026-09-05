import React, { JSX } from "react";
import { Button, Card, Col, Container, Modal, Row } from "react-bootstrap";
import JamModal from "../../components/JamModal/JamModal";
import { Link } from "react-router-dom";
import "./TermsConditions.scss";
import "../About/AboutPage.scss";

interface PrivacySectionProps {
	number: number;
	title: string;
	children: React.ReactNode;
}

const PrivacySection: React.FC<PrivacySectionProps> = ({ number, title, children }) => (
	<Card className="terms-section terms-default">
		<Card.Header className="terms-card-header">
			<span className="section-number">{number}</span>
			{title}
		</Card.Header>
		<Card.Body>{children}</Card.Body>
	</Card>
);

interface PrivacySubsectionProps {
	title: string;
	children: React.ReactNode;
}

const PrivacySubsection: React.FC<PrivacySubsectionProps> = ({ title, children }) => (
	<div className="terms-subsection">
		<h5 className="terms-subsection-title">{title}</h5>
		{children}
	</div>
);

export function PrivacyContent(): JSX.Element {
	return (
		<div className="terms-content">
			<Card>
				<Card.Body>
					<i className="bi bi-calendar-check me-2" />
					<strong>Last Updated:</strong> February 2026 &nbsp;·&nbsp; Applies to JAM V1.2.1 and SPREAD V1.0.0
				</Card.Body>
			</Card>

			<p className="terms-text mt-4">
				This Privacy Policy explains how Job Application Manager ("JAM", "we", "us") collects, uses, and
				protects your personal data when you use the JAM web application or the SPREAD Chrome extension. It is
				written in compliance with the UK General Data Protection Regulation (UK GDPR) and the Data Protection
				Act 2018. Our <Link to="/terms">Terms and Conditions</Link> are published separately.
			</p>

			<PrivacySection number={1} title="Data Controller">
				<p className="terms-text mb-0">
					The data controller for JAM is Emmanuel V. Péan. For any privacy-related enquiries, please contact
					us via the in-app support channel or the feedback feature.
				</p>
			</PrivacySection>

			<PrivacySection number={2} title="Data We Collect - JAM Web Application">
				<PrivacySubsection title="2.1 Account Information">
					<ul className="terms-list">
						<li>Email address, first name, and last name - provided at registration</li>
						<li>
							Password - stored as a one-way cryptographic hash; we never have access to your plain-text
							password
						</li>
					</ul>
				</PrivacySubsection>
				<PrivacySubsection title="2.2 Professional Profile (optional)">
					<ul className="terms-list">
						<li>Work experience, education history, skills, and career interests</li>
						<li>
							This data is used exclusively to power the AI job rating feature (premium) and is never used
							for advertising or sold to third parties
						</li>
					</ul>
				</PrivacySubsection>
				<PrivacySubsection title="2.3 Job Application Data">
					<ul className="terms-list">
						<li>
							Job records, company details, contacts, interviews, locations, and application notes you
							create within the app
						</li>
						<li>You retain full ownership of this data at all times</li>
					</ul>
				</PrivacySubsection>
				<PrivacySubsection title="2.4 Email Content (Premium)">
					<ul className="terms-list">
						<li>
							Job alert emails you forward to your designated JAM address are parsed to extract structured
							job data (title, company, salary, location)
						</li>
						<li>Email content is processed automatically and is not read by any person</li>
						<li>Raw email content is not retained after processing</li>
					</ul>
				</PrivacySubsection>
				<PrivacySubsection title="2.5 Usage Preferences">
					<ul className="terms-list">
						<li>
							App settings such as theme, dark mode preference, dashboard thresholds, and display
							preferences
						</li>
					</ul>
				</PrivacySubsection>
				<PrivacySubsection title="2.6 Data We Do NOT Collect">
					<ul className="terms-list">
						<li>We do not use cookies for tracking or advertising</li>
						<li>We do not collect IP addresses or device fingerprints</li>
						<li>We do not run any third-party analytics or advertising scripts</li>
						<li>We do not collect data from minors under 16</li>
					</ul>
				</PrivacySubsection>
			</PrivacySection>

			<PrivacySection number={3} title="Lawful Basis for Processing">
				<ul className="terms-list">
					<li>
						<strong>Contract (Article 6(1)(b)):</strong> Processing your account information, job data, and
						preferences is necessary to provide the JAM service you have signed up for.
					</li>
					<li>
						<strong>Legitimate Interests (Article 6(1)(f)):</strong> We may use anonymised, aggregated usage
						patterns to improve the service. No personal data is shared externally for this purpose.
					</li>
					<li>
						<strong>Consent (Article 6(1)(a)):</strong> For premium email processing, you explicitly enable
						this feature. You can withdraw consent at any time by cancelling your premium subscription.
					</li>
				</ul>
			</PrivacySection>

			<PrivacySection number={4} title="How We Use Your Data">
				<ul className="terms-list">
					<li>To create and manage your account</li>
					<li>To provide the core job tracking features of JAM</li>
					<li>To process job alert emails and present extracted jobs in your dashboard (premium)</li>
					<li>
						To power AI job rating by sending job descriptions and your qualifications to Anthropic's API
						(premium)
					</li>
					<li>
						To send transactional emails: account verification, password resets, and subscription notices
					</li>
					<li>To process subscription payments via Stripe</li>
					<li>We do not sell, rent, or share your personal data with third parties for marketing</li>
				</ul>
			</PrivacySection>

			<PrivacySection number={5} title="Data Processors & Third Parties">
				<p className="terms-text">
					We share data with the following processors only to the extent necessary to deliver the service:
				</p>
				<PrivacySubsection title="5.1 Anthropic (AI Job Rating - Premium)">
					<p className="terms-text mb-0">
						Job descriptions and your qualifications profile are sent to Anthropic's API to generate job
						ratings. Data is processed under Anthropic's API data usage policy. Anthropic does not use API
						data to train its models by default.
					</p>
				</PrivacySubsection>
				<PrivacySubsection title="5.2 Stripe (Payments)">
					<p className="terms-text mb-0">
						All payment data is handled directly by Stripe. We store only a Stripe Customer ID and
						subscription status - never card numbers or full payment details.
					</p>
				</PrivacySubsection>
				<PrivacySubsection title="5.3 Apify & BrightData (Job Data - Premium)">
					<p className="terms-text mb-0">
						These services are used to enrich job posting data scraped from job boards. Personal data (your
						name, email, qualifications) is never shared with these providers.
					</p>
				</PrivacySubsection>
				<PrivacySubsection title="5.4 Hostinger (Email Delivery)">
					<p className="terms-text mb-0">
						Transactional emails (verification, password reset, subscription notices) are sent via Hostinger
						SMTP. Only your email address is shared for delivery purposes.
					</p>
				</PrivacySubsection>
			</PrivacySection>

			<PrivacySection number={6} title="Data Retention">
				<ul className="terms-list">
					<li>
						<strong>Account data:</strong> Retained until you delete it or close your account.
					</li>
					<li>
						<strong>Processed email content:</strong> Raw email content is discarded after processing.
					</li>
					<li>
						<strong>Payment records:</strong> Stripe retains billing records subject to their own retention
						policy and applicable financial regulations.
					</li>
				</ul>
			</PrivacySection>

			<PrivacySection number={7} title="International Data Transfers">
				<p className="terms-text mb-0">
					JAM is hosted in the UK. Some third-party processors (Anthropic, Stripe, Apify, BrightData) operate
					in the United States. Where personal data is transferred outside the UK, we rely on Standard
					Contractual Clauses or the processor's UK adequacy arrangements to ensure an equivalent level of
					protection.
				</p>
			</PrivacySection>

			<PrivacySection number={8} title="Your Rights Under UK GDPR">
				<p className="terms-text">You have the following rights regarding your personal data:</p>
				<ul className="terms-list">
					<li>
						<strong>Right of Access:</strong> Request a copy of the personal data we hold about you
					</li>
					<li>
						<strong>Right to Rectification:</strong> Correct inaccurate or incomplete data directly in your
						account settings
					</li>
					<li>
						<strong>Right to Erasure:</strong> Delete your account and all associated data at any time via
						account settings
					</li>
					<li>
						<strong>Right to Data Portability:</strong> Export all your data as CSV files via account
						settings at any time
					</li>
					<li>
						<strong>Right to Restrict Processing:</strong> Request that we limit how we use your data in
						certain circumstances
					</li>
					<li>
						<strong>Right to Object:</strong> Object to processing based on legitimate interests
					</li>
					<li>
						<strong>Right to Complain:</strong> Lodge a complaint with the Information Commissioner's Office
						(ICO) at{" "}
						<a href="https://ico.org.uk" target="_blank" rel="noopener noreferrer">
							ico.org.uk
						</a>{" "}
						if you believe your data has been handled unlawfully
					</li>
				</ul>
				<p className="terms-text mb-0">
					To exercise any of these rights, please contact us via the in-app support channel. We will respond
					within 30 days.
				</p>
			</PrivacySection>

			<PrivacySection number={9} title="Cookies & Local Storage">
				<ul className="terms-list">
					<li>JAM does not use cookies for tracking, advertising, or analytics</li>
					<li>
						Your authentication token (JWT) is stored in browser local storage to keep you logged in. It
						contains your user ID and account type - no sensitive personal data
					</li>
					<li>
						App preferences (theme, display settings) are stored in your browser's local storage for
						performance. This data never leaves your device
					</li>
				</ul>
			</PrivacySection>

			<PrivacySection number={10} title="SPREAD Chrome Extension - Privacy">
				<p className="terms-text">
					SPREAD is an optional browser extension. It operates entirely separately from the JAM server and
					handles data as follows:
				</p>
				<PrivacySubsection title="10.1 Data Accessed">
					<ul className="terms-list">
						<li>
							<strong>Active tab URL:</strong> Read once when you open the popup to detect whether the
							current page is a supported job listing. Never stored or transmitted.
						</li>
						<li>
							<strong>Job listing page content:</strong> When you click "Save to JAM", the extension reads
							the visible page to extract: job title, company, salary, location, attendance type,
							deadline, and description.
						</li>
					</ul>
				</PrivacySubsection>
				<PrivacySubsection title="10.2 Data We Do NOT Collect">
					<ul className="terms-list">
						<li>Browsing history or pages other than the active job listing</li>
						<li>Personal identifiable information (name, address, age)</li>
						<li>Authentication credentials or passwords</li>
						<li>Financial or payment information</li>
						<li>Any data from non-job-listing pages</li>
					</ul>
				</PrivacySubsection>
				<PrivacySubsection title="10.3 How Extracted Data Is Used">
					<ul className="terms-list">
						<li>Extracted job data is sent directly and exclusively to your own JAM instance</li>
						<li>
							No data is sent to any server, analytics service, or external endpoint operated by us or any
							third party
						</li>
						<li>
							If no JAM tab is open, data is temporarily saved to <code>chrome.storage.local</code> on
							your device and cleared immediately after being read by JAM
						</li>
					</ul>
				</PrivacySubsection>
				<PrivacySubsection title="10.4 Permissions Justification">
					<ul className="terms-list">
						<li>
							<strong>activeTab:</strong> Detect supported job pages and read their content
						</li>
						<li>
							<strong>scripting:</strong> Inject the content script that extracts job details from the
							page DOM
						</li>
						<li>
							<strong>tabs:</strong> Find or create a JAM tab to receive the job data
						</li>
						<li>
							<strong>storage:</strong> Temporarily hold extracted data on your device when no JAM tab is
							open
						</li>
						<li>
							<strong>Host permissions</strong> (LinkedIn, Indeed, NHS Jobs, VeganJobs): Required by
							Chrome to allow script injection on those specific domains
						</li>
					</ul>
				</PrivacySubsection>
				<PrivacySubsection title="10.5 No Remote Code">
					<p className="terms-text mb-0">
						SPREAD does not load or execute remote code. All scripts are bundled locally within the
						extension package and are not fetched from any external server at runtime.
					</p>
				</PrivacySubsection>
			</PrivacySection>

			<PrivacySection number={11} title="Changes to This Policy">
				<p className="terms-text mb-0">
					We may update this Privacy Policy from time to time. When we do, we will update the "Last Updated"
					date at the top and, for material changes, notify you via the in-app release notes or email.
					Continued use of the Service after changes are posted constitutes acceptance of the updated policy.
				</p>
			</PrivacySection>

			<PrivacySection number={12} title="Contact">
				<p className="terms-text mb-0">
					For any questions about this Privacy Policy or to exercise your data rights, please contact us via
					the in-app support channel. You may also review our <Link to="/terms">Terms and Conditions</Link>.
				</p>
			</PrivacySection>
		</div>
	);
}

interface PrivacyPolicyModalProps {
	show: boolean;
	onHide: () => void;
}

export function PrivacyPolicyModal({ show, onHide }: PrivacyPolicyModalProps): JSX.Element {
	return (
		<JamModal show={show} onHide={onHide} scrollable className="terms-modal">
			<Modal.Header closeButton className="terms-header">
				<Modal.Title className="d-flex align-items-center">
					<i className="bi bi-shield-check me-2"></i>
					Privacy Policy
				</Modal.Title>
			</Modal.Header>
			<Modal.Body className="terms-body">
				<PrivacyContent />
			</Modal.Body>
			<Modal.Footer className="terms-footer">
				<Button variant="primary" onClick={onHide} style={{ width: "100%" }}>
					<i className="bi bi-check-circle me-2"></i>I Understand and Accept
				</Button>
			</Modal.Footer>
		</JamModal>
	);
}

const PrivacyPolicyPage = (): JSX.Element => (
	<div style={{ borderRadius: "18px", overflow: "hidden", minHeight: "100%" }}>
		<Container className="py-5">
			<Row className="justify-content-center mb-4">
				<Col lg={8} className="text-center">
					<i className="bi bi-shield-check" style={{ fontSize: "3rem", color: "var(--primary-mid)" }} />
					<h1 className="display-5 fw-bold mt-3">Privacy Policy</h1>
					<p className="about-text-muted mt-2">JAM &amp; SPREAD Chrome Extension</p>
				</Col>
			</Row>

			<Row className="justify-content-center">
				<Col lg={10}>
					<PrivacyContent />
				</Col>
			</Row>
		</Container>
	</div>
);

export default PrivacyPolicyPage;
