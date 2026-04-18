import React, { JSX } from "react";
import { Button, Card, Modal } from "react-bootstrap";
import JamModal from "../../components/JamModal/JamModal";
import { Link } from "react-router-dom";
import "./TermsConditions.scss";
import { PREMIUM_PRICE } from "../UserSettings/PremiumTab";

interface TermsSectionProps {
	number: number;
	title: string;
	children: React.ReactNode;
}

const TermsSection: React.FC<TermsSectionProps> = ({ number, title, children }: TermsSectionProps): JSX.Element => (
	<Card className="terms-section terms-default">
		<Card.Header className="terms-card-header">
			<span className="section-number">{number}</span>
			{title}
		</Card.Header>
		<Card.Body>{children}</Card.Body>
	</Card>
);

interface TermsSubsectionProps {
	title: string;
	children: React.ReactNode;
}

const TermsSubsection: React.FC<TermsSubsectionProps> = ({ title, children }) => (
	<div className="terms-subsection">
		<h5 className="terms-subsection-title">{title}</h5>
		{children}
	</div>
);

export function TermsContent(): JSX.Element {
	return (
		<div className="terms-content">
			<Card>
				<Card.Body>
					<i className="bi bi-calendar-check me-2"></i>
					<strong>Last Updated:</strong> February 2026
				</Card.Body>
			</Card>

			<TermsSection number={1} title="Acceptance of Terms">
				<p className="terms-text">
					By accessing and using the Job Application Manager ("JAM", "the Service"), you accept and agree to
					be bound by these Terms and Conditions and our <Link to="/privacy">Privacy Policy</Link>. If you do
					not agree, please do not use this Service. We reserve the right to update these terms at any time,
					and continued use of the Service constitutes acceptance of any modifications.
				</p>
			</TermsSection>

			<TermsSection number={2} title="Description of Service">
				<p className="terms-text">
					JAM is a web-based application designed to help users organise and track their job applications,
					interviews, and career management activities.
				</p>
				<TermsSubsection title="2.1 Free Features">
					<ul className="terms-list">
						<li>Create and manage job application records with detailed tracking</li>
						<li>Track interview schedules, outcomes, and interviewer information</li>
						<li>Store company, location, and recruiter contact information</li>
						<li>Monitor application status, deadlines, and follow-up reminders</li>
						<li>Export all your data at any time</li>
					</ul>
				</TermsSubsection>
				<TermsSubsection title="2.2 Premium Features (TOAST Subscription)">
					<ul className="terms-list">
						<li>
							<strong>Automated Email Scraping:</strong> Extract job postings from LinkedIn, Indeed, NHS
							Jobs, and other job alert emails
						</li>
						<li>
							<strong>AI-Powered Job Rating:</strong> Intelligent matching of jobs against your
							qualifications using artificial intelligence
						</li>
						<li>
							<strong>Smart Filtering:</strong> Advanced exclusion and favourite filters for job alerts
						</li>
					</ul>
				</TermsSubsection>
				<TermsSubsection title="2.3 SPREAD Chrome Extension">
					<p className="terms-text mb-0">
						SPREAD (Smart Plugin for Recruitment Extraction &amp; Aggregation of Data) is an optional Chrome
						browser extension that lets you import job listings from supported job boards directly into JAM.
						For full details on how SPREAD handles your data, see our{" "}
						<Link to="/privacy">Privacy Policy</Link>.
					</p>
				</TermsSubsection>
			</TermsSection>

			<TermsSection number={3} title="Subscription and Payment">
				<TermsSubsection title="3.1 TOAST Premium Subscription">
					<ul className="terms-list">
						<li>
							<strong>Price:</strong> {PREMIUM_PRICE} per month (GBP)
						</li>
						<li>
							<strong>Free Trial:</strong> New customers receive a 14-day free trial with no payment
							method required
						</li>
						<li>
							<strong>Returning Customers:</strong> Users who have previously subscribed are not eligible
							for a free trial and must provide payment details upfront
						</li>
						<li>Subscriptions automatically renew monthly unless cancelled</li>
					</ul>
				</TermsSubsection>
				<TermsSubsection title="3.2 Cancellation and Refunds">
					<ul className="terms-list">
						<li>You may cancel your subscription at any time via the Stripe Customer Portal</li>
						<li>
							Upon cancellation, you retain access to premium features until the end of your current
							billing period
						</li>
						<li>Refunds are not provided for partial months or unused portions of your subscription</li>
						<li>
							If your trial ends without adding a payment method, premium features will be disabled
							automatically
						</li>
					</ul>
				</TermsSubsection>
				<TermsSubsection title="3.3 Payment Processing">
					<p className="terms-text mb-0">
						All payments are processed securely through Stripe. We do not store your full credit card
						details on our servers. By subscribing, you agree to Stripe's terms of service.
					</p>
				</TermsSubsection>
			</TermsSection>

			<TermsSection number={4} title="User Accounts">
				<TermsSubsection title="4.1 Registration">
					<ul className="terms-list">
						<li>You must provide accurate, complete, and current information during registration</li>
						<li>Email verification is required to activate your account</li>
						<li>You are responsible for maintaining the confidentiality of your account credentials</li>
						<li>You are responsible for all activities that occur under your account</li>
						<li>You must be at least 16 years old to use this Service</li>
					</ul>
				</TermsSubsection>
				<TermsSubsection title="4.2 Account Security">
					<ul className="terms-list">
						<li>Choose a strong password and keep it secure</li>
						<li>Notify us immediately of any unauthorised use of your account</li>
						<li>We use industry-standard password hashing to protect your credentials</li>
						<li>
							We are not liable for any loss arising from unauthorised account access due to your failure
							to protect your credentials
						</li>
					</ul>
				</TermsSubsection>
			</TermsSection>

			<TermsSection number={5} title="Third-Party Services">
				<p className="terms-text">
					JAM integrates with the following third-party services to provide its functionality:
				</p>
				<TermsSubsection title="5.1 AI Services">
					<p className="terms-text mb-0">
						Our AI job rating feature uses <strong>Anthropic's API</strong> to analyse job descriptions and
						match them against your qualifications. Relevant job and qualification data is sent to Anthropic
						for processing. Anthropic's data retention and privacy policies apply.
					</p>
				</TermsSubsection>
				<TermsSubsection title="5.2 Payment Processing">
					<p className="terms-text mb-0">
						Subscription payments are handled by <strong>Stripe</strong>. Your payment information is
						processed directly by Stripe and is subject to their privacy policy and terms of service.
					</p>
				</TermsSubsection>
				<TermsSubsection title="5.3 Job Data Providers">
					<p className="terms-text mb-0">
						Premium features utilise <strong>Apify</strong> and <strong>BrightData</strong> to collect and
						enrich job posting data from various platforms. Their respective privacy policies and terms of
						service apply to data processed through their platforms.
					</p>
				</TermsSubsection>
			</TermsSection>

			<TermsSection number={6} title="Acceptable Use">
				<p className="terms-text">You agree NOT to use the Service to:</p>
				<ul className="terms-list">
					<li>Upload malicious code, viruses, or harmful content</li>
					<li>Attempt to gain unauthorised access to our systems or other users' accounts</li>
					<li>Share false, misleading, or fraudulent information</li>
					<li>Violate any applicable laws or regulations</li>
					<li>Interfere with other users' use of the Service</li>
					<li>Use automated tools to scrape or access the Service beyond intended functionality</li>
					<li>Resell, redistribute, or commercially exploit the Service without authorisation</li>
					<li>Use the Service to spam employers or send unsolicited communications</li>
				</ul>
			</TermsSection>

			<TermsSection number={7} title="Service Availability">
				<TermsSubsection title="7.1 Uptime and Maintenance">
					<ul className="terms-list">
						<li>We strive to maintain high service availability but do not guarantee 100% uptime</li>
						<li>We may perform maintenance that temporarily interrupts service</li>
						<li>We will provide advance notice of planned maintenance when possible</li>
					</ul>
				</TermsSubsection>
				<TermsSubsection title="7.2 Third-Party Dependencies">
					<p className="terms-text mb-0">
						Premium features depend on third-party APIs (Anthropic, job platforms, data providers). We
						cannot guarantee the availability or accuracy of these external services. Changes to third-party
						platforms may affect feature functionality.
					</p>
				</TermsSubsection>
				<TermsSubsection title="7.3 Service Modifications">
					<ul className="terms-list">
						<li>We reserve the right to modify, suspend, or discontinue features</li>
						<li>We will provide reasonable notice of significant changes</li>
						<li>Continued use after changes constitutes acceptance of modifications</li>
					</ul>
				</TermsSubsection>
			</TermsSection>

			<TermsSection number={8} title="Limitation of Liability">
				<p className="terms-text">
					<strong>TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW:</strong>
				</p>
				<ul className="terms-list">
					<li>
						THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR
						IMPLIED
					</li>
					<li>WE DO NOT WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED, SECURE, OR ERROR-FREE</li>
					<li>WE ARE NOT LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES</li>
					<li>
						OUR TOTAL LIABILITY IS LIMITED TO THE AMOUNT YOU PAID FOR THE SERVICE IN THE 12 MONTHS PRECEDING
						THE CLAIM
					</li>
					<li>
						WE ARE NOT RESPONSIBLE FOR DATA LOSS, THOUGH WE IMPLEMENT REASONABLE SAFEGUARDS. YOU ARE
						RESPONSIBLE FOR MAINTAINING YOUR OWN BACKUPS
					</li>
					<li>
						WE ARE NOT LIABLE FOR ANY EMPLOYMENT DECISIONS, JOB OUTCOMES, OR CAREER CONSEQUENCES RESULTING
						FROM YOUR USE OF THE SERVICE
					</li>
					<li>
						AI-GENERATED JOB RATINGS AND RECOMMENDATIONS ARE PROVIDED FOR INFORMATIONAL PURPOSES ONLY AND
						SHOULD NOT BE RELIED UPON AS THE SOLE BASIS FOR CAREER DECISIONS
					</li>
					<li>
						WE ARE NOT RESPONSIBLE FOR THE ACCURACY, COMPLETENESS, OR AVAILABILITY OF JOB DATA OBTAINED FROM
						THIRD-PARTY SOURCES
					</li>
				</ul>
			</TermsSection>

			<TermsSection number={9} title="Indemnification">
				<p className="terms-text">
					You agree to indemnify, defend, and hold harmless JAM, its operators, and affiliates from any
					claims, damages, losses, liabilities, and expenses (including legal fees) arising from:
				</p>
				<ul className="terms-list">
					<li>Your use or misuse of the Service</li>
					<li>Your violation of these Terms and Conditions</li>
					<li>Your violation of any third-party rights, including intellectual property rights</li>
					<li>Your violation of any applicable laws or regulations</li>
					<li>Any content or data you submit to the Service</li>
				</ul>
			</TermsSection>

			<TermsSection number={10} title="Termination">
				<TermsSubsection title="10.1 Termination by You">
					<ul className="terms-list">
						<li>You may delete your account at any time through account settings</li>
						<li>You may export your data before deletion</li>
						<li>Active subscriptions will be automatically cancelled upon account deletion</li>
					</ul>
				</TermsSubsection>
				<TermsSubsection title="10.2 Termination by Us">
					<ul className="terms-list">
						<li>We may suspend or terminate accounts that violate these terms</li>
						<li>We may terminate the Service with 30 days' notice</li>
						<li>We will provide data export opportunities before service termination</li>
						<li>Termination does not entitle you to refunds for paid subscription periods</li>
					</ul>
				</TermsSubsection>
			</TermsSection>

			<TermsSection number={11} title="General Provisions">
				<TermsSubsection title="11.1 Governing Law">
					<p className="terms-text mb-0">
						These terms are governed by the laws of England and Wales. Any disputes shall be subject to the
						exclusive jurisdiction of the courts of England and Wales.
					</p>
				</TermsSubsection>
				<TermsSubsection title="11.2 Severability">
					<p className="terms-text mb-0">
						If any provision of these terms is found to be unenforceable or invalid, that provision shall be
						limited or eliminated to the minimum extent necessary, and the remaining provisions shall remain
						in full force and effect.
					</p>
				</TermsSubsection>
				<TermsSubsection title="11.3 Entire Agreement">
					<p className="terms-text mb-0">
						These Terms and Conditions, together with the <Link to="/privacy">Privacy Policy</Link>,
						constitute the entire agreement between you and JAM regarding use of the Service, superseding
						any prior agreements.
					</p>
				</TermsSubsection>
				<TermsSubsection title="11.4 Contact">
					<p className="terms-text mb-0">
						For questions about these terms or the Service, please contact us through the application's
						feedback feature or support channels.
					</p>
				</TermsSubsection>
			</TermsSection>
		</div>
	);
}

interface TermsAndConditionsProps {
	show: boolean;
	onHide: () => void;
}

function TermsAndConditions({ show, onHide }: TermsAndConditionsProps): JSX.Element {
	return (
		<JamModal show={show} onHide={onHide} scrollable className="terms-modal">
			<Modal.Header closeButton className="terms-header">
				<Modal.Title className="d-flex align-items-center">
					<i className="bi bi-file-earmark-text me-2"></i>
					Terms and Conditions
				</Modal.Title>
			</Modal.Header>
			<Modal.Body className="terms-body">
				<TermsContent />
			</Modal.Body>
			<Modal.Footer className="terms-footer">
				<Button variant="primary" onClick={onHide} style={{ width: "100%" }}>
					<i className="bi bi-check-circle me-2"></i>I Understand and Accept
				</Button>
			</Modal.Footer>
		</JamModal>
	);
}

export default TermsAndConditions;
