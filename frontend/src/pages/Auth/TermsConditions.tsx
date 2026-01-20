import React, { JSX } from "react";
import { Modal, Button } from "react-bootstrap";
import "./TermsConditions.css";

interface TermsAndConditionsProps {
	show: boolean;
	onHide: () => void;
}

function TermsAndConditions({ show, onHide }: TermsAndConditionsProps): JSX.Element {
	return (
		<Modal show={show} onHide={onHide} scrollable className="terms-modal">
			<Modal.Header closeButton className="terms-header">
				<Modal.Title className="d-flex align-items-center">
					<i className="bi bi-file-text me-2"></i>
					Terms and Conditions
				</Modal.Title>
			</Modal.Header>
			<Modal.Body className="terms-body">
				<div className="terms-content">
					<div className="terms-section">
						<h4 className="terms-section-title">
							<span className="section-number">1.</span>
							Acceptance of Terms
						</h4>
						<p className="terms-text">
							By accessing and using the Job Application Manager ("the Service"), you accept and agree to
							be bound by the terms and provision of this agreement. If you do not agree to abide by the
							above, please do not use this service.
						</p>
					</div>

					<div className="terms-section">
						<h4 className="terms-section-title">
							<span className="section-number">2.</span>
							Description of Service
						</h4>
						<p className="terms-text">
							Job Application Manager is a web-based application that helps users organise and track their
							job applications, interviews, and related career management activities. The Service allows
							you to:
						</p>
						<ul className="terms-list">
							<li>Create and manage job application records</li>
							<li>Track interview schedules and outcomes</li>
							<li>Store company and contact information</li>
							<li>Monitor application status, progress, and deadline</li>
						</ul>
					</div>

					<div className="terms-section">
						<h4 className="terms-section-title">
							<span className="section-number">3.</span>
							User Accounts
						</h4>
						<div className="terms-subsection">
							<h5 className="terms-subsection-title">3.1 Registration</h5>
							<ul className="terms-list">
								<li>
									You must provide accurate, complete, and up-to-date information during registration
								</li>
								<li>
									You are responsible for maintaining the confidentiality of your account credentials
								</li>
								<li>You are responsible for all activities that occur under your account</li>
							</ul>
						</div>

						<div className="terms-subsection">
							<h5 className="terms-subsection-title">3.2 Account Security</h5>
							<ul className="terms-list">
								<li>Choose a strong password and keep it secure</li>
								<li>Notify us immediately of any unauthorised use of your account</li>
								<li>
									We are not liable for any loss or damage arising from unauthorised account access
								</li>
							</ul>
						</div>
					</div>

					<div className="terms-section">
						<h4 className="terms-section-title">
							<span className="section-number">4.</span>
							User Content and Data
						</h4>
						<div className="terms-subsection">
							<h5 className="terms-subsection-title">4.1 Your Data</h5>
							<ul className="terms-list">
								<li>You retain ownership of all data you submit to the Service</li>
								<li>
									You grant us a limited license to store, process, and display your data to provide
									the Service
								</li>
								<li>You are responsible for backing up your data</li>
							</ul>
						</div>

						<div className="terms-subsection">
							<h5 className="terms-subsection-title">4.2 Data Usage</h5>
							<ul className="terms-list">
								<li>We will not share your personal job application data with third parties.</li>
								<li>We may use aggregated, anonymised data for service improvement and analytics</li>
								<li>You may export or delete your data at any time</li>
							</ul>
						</div>
					</div>

					<div className="terms-section">
						<h4 className="terms-section-title">
							<span className="section-number">5.</span>
							Acceptable Use
						</h4>
						<p className="terms-text">You agree NOT to use the Service to:</p>
						<ul className="terms-list terms-prohibited">
							<li>Upload malicious code, viruses, or harmful content</li>
							<li>Attempt to gain unauthorised access to our systems</li>
							<li>Share false, misleading, or inaccurate information</li>
							<li>Violate any applicable laws or regulations</li>
							<li>Interfere with other users' use of the Service</li>
						</ul>
					</div>

					<div className="terms-section">
						<h4 className="terms-section-title">
							<span className="section-number">6.</span>
							Privacy
						</h4>
						<p className="terms-text">
							Your privacy is important to us. Our data handling practices are governed by our Privacy
							Policy, which is incorporated into these terms by reference. Key points:
						</p>
						<ul className="terms-list">
							<li>We collect only necessary information to provide the Service</li>
							<li>We use industry-standard security measures to protect your data</li>
							<li>We do not sell your personal information to third parties</li>
							<li>You can request data deletion at any time</li>
						</ul>
					</div>

					<div className="terms-section">
						<h4 className="terms-section-title">
							<span className="section-number">7.</span>
							Service Availability
						</h4>
						<div className="terms-subsection">
							<h5 className="terms-subsection-title">7.1 Uptime</h5>
							<ul className="terms-list">
								<li>
									We strive to maintain high service availability but do not guarantee 100% uptime
								</li>
								<li>We may perform maintenance that temporarily interrupts service</li>
								<li>We will provide advance notice of planned maintenance when possible</li>
							</ul>
						</div>

						<div className="terms-subsection">
							<h5 className="terms-subsection-title">7.2 Service Modifications</h5>
							<ul className="terms-list">
								<li>We reserve the right to modify, suspend, or discontinue the Service</li>
								<li>We will provide reasonable notice of significant changes</li>
								<li>Continued use after changes constitutes acceptance of modifications</li>
							</ul>
						</div>
					</div>

					<div className="terms-section">
						<h4 className="terms-section-title">
							<span className="section-number">8.</span>
							Intellectual Property
						</h4>
						<div className="terms-subsection">
							<h5 className="terms-subsection-title">8.1 Your Rights</h5>
							<ul className="terms-list">
								<li>You retain rights to your data and content</li>
								<li>We grant you a limited license to use the Service for its intended purpose</li>
							</ul>
						</div>
					</div>

					<div className="terms-section">
						<h4 className="terms-section-title">
							<span className="section-number">9.</span>
							Limitation of Liability
						</h4>
						<p className="terms-text">
							<strong>TO THE MAXIMUM EXTENT PERMITTED BY LAW:</strong>
						</p>
						<ul className="terms-list">
							<li>THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES</li>
							<li>WE ARE NOT LIABLE FOR INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES</li>
							<li>OUR TOTAL LIABILITY IS LIMITED TO THE AMOUNT YOU PAID FOR THE SERVICE</li>
							<li>WE ARE NOT RESPONSIBLE FOR DATA LOSS, THOUGH WE IMPLEMENT REASONABLE SAFEGUARDS</li>
						</ul>
					</div>

					<div className="terms-section">
						<h4 className="terms-section-title">
							<span className="section-number">10.</span>
							Indemnification
						</h4>
						<p className="terms-text">
							You agree to indemnify and hold us harmless from any claims, damages, or losses arising
							from:
						</p>
						<ul className="terms-list">
							<li>Your use of the Service</li>
							<li>Your violation of these terms</li>
							<li>Your violation of any third-party rights</li>
						</ul>
					</div>

					<div className="terms-section">
						<h4 className="terms-section-title">
							<span className="section-number">11.</span>
							Termination
						</h4>
						<div className="terms-subsection">
							<h5 className="terms-subsection-title">11.1 By You</h5>
							<ul className="terms-list">
								<li>You may terminate your account at any time</li>
								<li>Upon termination, you may export your data</li>
								<li>Some provisions of these terms survive termination</li>
							</ul>
						</div>

						<div className="terms-subsection">
							<h5 className="terms-subsection-title">11.2 By Us</h5>
							<ul className="terms-list">
								<li>We may terminate accounts that violate these terms</li>
								<li>We may terminate the Service with reasonable notice</li>
								<li>We will provide data export opportunities before termination</li>
							</ul>
						</div>
					</div>

					<div className="terms-section">
						<h4 className="terms-section-title">
							<span className="section-number">12.</span>
							Dispute Resolution
						</h4>
						<div className="terms-subsection">
							<h5 className="terms-subsection-title">12.1 Governing Law</h5>
							<p className="terms-text">These terms are governed by applicable local laws.</p>
						</div>
					</div>

					<div className="terms-section">
						<h4 className="terms-section-title">
							<span className="section-number">13.</span>
							General Provisions
						</h4>
						<div className="terms-subsection">
							<h5 className="terms-subsection-title">13.1 Entire Agreement</h5>
							<p className="terms-text">
								These terms constitute the entire agreement between you and us regarding the Service.
							</p>
						</div>

						<div className="terms-subsection">
							<h5 className="terms-subsection-title">13.2 Severability</h5>
							<p className="terms-text">
								If any provision is found unenforceable, the remaining provisions remain in effect.
							</p>
						</div>

						<div className="terms-subsection">
							<h5 className="terms-subsection-title">13.3 Updates</h5>
							<p className="terms-text">
								We may update these terms periodically. Continued use constitutes acceptance of changes.
							</p>
						</div>

						<div className="terms-subsection">
							<h5 className="terms-subsection-title">13.4 Contact</h5>
							<p className="terms-text">
								For questions about these terms, please contact us through the application.
							</p>
						</div>
					</div>
				</div>
			</Modal.Body>
			<Modal.Footer className="terms-footer">
				<Button variant="primary" onClick={onHide} style={{ width: "100%" }}>
					<i className="bi bi-check-circle me-2"></i>I Understand
				</Button>
			</Modal.Footer>
		</Modal>
	);
}

export default TermsAndConditions;
