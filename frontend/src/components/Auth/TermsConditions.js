import React from "react";
import { Modal, Button } from "react-bootstrap";

function TermsAndConditions({ show, onHide }) {
	return (
		<Modal show={show} onHide={onHide} size="lg" scrollable>
			<Modal.Header closeButton>
				<Modal.Title>Terms and Conditions</Modal.Title>
			</Modal.Header>
			<Modal.Body style={{ maxHeight: "70vh" }}>
				<div className="terms-content">
					<p><strong>Last updated: {new Date().toLocaleDateString()}</strong></p>

					<h4>1. Acceptance of Terms</h4>
					<p>
						By accessing and using the Job Application Manager ("the Service"), you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by the above, please do not use this service.
					</p>

					<h4>2. Description of Service</h4>
					<p>
						Job Application Manager is a web-based application that helps users organize and track their job applications, interviews, and related career management activities. The Service allows you to:
					</p>
					<ul>
						<li>Create and manage job application records</li>
						<li>Track interview schedules and outcomes</li>
						<li>Store company and contact information</li>
						<li>Monitor application status and progress</li>
						<li>Generate reports and analytics on your job search</li>
					</ul>

					<h4>3. User Accounts</h4>
					<h5>3.1 Registration</h5>
					<ul>
						<li>You must provide accurate, complete, and up-to-date information during registration</li>
						<li>You are responsible for maintaining the confidentiality of your account credentials</li>
						<li>You are responsible for all activities that occur under your account</li>
					</ul>

					<h5>3.2 Account Security</h5>
					<ul>
						<li>Choose a strong password and keep it secure</li>
						<li>Notify us immediately of any unauthorized use of your account</li>
						<li>We are not liable for any loss or damage arising from unauthorized account access</li>
					</ul>

					<h4>4. User Content and Data</h4>
					<h5>4.1 Your Data</h5>
					<ul>
						<li>You retain ownership of all data you submit to the Service</li>
						<li>You grant us a limited license to store, process, and display your data to provide the Service</li>
						<li>You are responsible for backing up your data</li>
					</ul>

					<h5>4.2 Data Usage</h5>
					<ul>
						<li>We will not share your personal job application data with third parties without your consent</li>
						<li>We may use aggregated, anonymized data for service improvement and analytics</li>
						<li>You may export or delete your data at any time</li>
					</ul>

					<h4>5. Acceptable Use</h4>
					<p>You agree NOT to use the Service to:</p>
					<ul>
						<li>Upload malicious code, viruses, or harmful content</li>
						<li>Attempt to gain unauthorized access to our systems</li>
						<li>Share false, misleading, or inaccurate information</li>
						<li>Violate any applicable laws or regulations</li>
						<li>Interfere with other users' use of the Service</li>
					</ul>

					<h4>6. Privacy</h4>
					<p>
						Your privacy is important to us. Our data handling practices are governed by our Privacy Policy, which is incorporated into these terms by reference. Key points:
					</p>
					<ul>
						<li>We collect only necessary information to provide the Service</li>
						<li>We use industry-standard security measures to protect your data</li>
						<li>We do not sell your personal information to third parties</li>
						<li>You can request data deletion at any time</li>
					</ul>

					<h4>7. Service Availability</h4>
					<h5>7.1 Uptime</h5>
					<ul>
						<li>We strive to maintain high service availability but do not guarantee 100% uptime</li>
						<li>We may perform maintenance that temporarily interrupts service</li>
						<li>We will provide advance notice of planned maintenance when possible</li>
					</ul>

					<h5>7.2 Service Modifications</h5>
					<ul>
						<li>We reserve the right to modify, suspend, or discontinue the Service</li>
						<li>We will provide reasonable notice of significant changes</li>
						<li>Continued use after changes constitutes acceptance of modifications</li>
					</ul>

					<h4>8. Intellectual Property</h4>
					<h5>8.1 Our Rights</h5>
					<ul>
						<li>The Service, including its design, code, and functionality, is our intellectual property</li>
						<li>Our trademarks, logos, and brand elements are protected</li>
					</ul>

					<h5>8.2 Your Rights</h5>
					<ul>
						<li>You retain rights to your data and content</li>
						<li>We grant you a limited license to use the Service for its intended purpose</li>
					</ul>

					<h4>9. Limitation of Liability</h4>
					<p><strong>TO THE MAXIMUM EXTENT PERMITTED BY LAW:</strong></p>
					<ul>
						<li>THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES</li>
						<li>WE ARE NOT LIABLE FOR INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES</li>
						<li>OUR TOTAL LIABILITY IS LIMITED TO THE AMOUNT YOU PAID FOR THE SERVICE</li>
						<li>WE ARE NOT RESPONSIBLE FOR DATA LOSS, THOUGH WE IMPLEMENT REASONABLE SAFEGUARDS</li>
					</ul>

					<h4>10. Indemnification</h4>
					<p>You agree to indemnify and hold us harmless from any claims, damages, or losses arising from:</p>
					<ul>
						<li>Your use of the Service</li>
						<li>Your violation of these terms</li>
						<li>Your violation of any third-party rights</li>
					</ul>

					<h4>11. Termination</h4>
					<h5>11.1 By You</h5>
					<ul>
						<li>You may terminate your account at any time</li>
						<li>Upon termination, you may export your data</li>
						<li>Some provisions of these terms survive termination</li>
					</ul>

					<h5>11.2 By Us</h5>
					<ul>
						<li>We may terminate accounts that violate these terms</li>
						<li>We may terminate the Service with reasonable notice</li>
						<li>We will provide data export opportunities before termination</li>
					</ul>

					<h4>12. Dispute Resolution</h4>
					<h5>12.1 Governing Law</h5>
					<p>These terms are governed by applicable local laws.</p>

					<h5>12.2 Dispute Process</h5>
					<ul>
						<li>First, contact us to resolve disputes informally</li>
						<li>If informal resolution fails, disputes will be resolved through appropriate legal channels</li>
						<li>You retain the right to pursue claims in small claims court where applicable</li>
					</ul>

					<h4>13. General Provisions</h4>
					<h5>13.1 Entire Agreement</h5>
					<p>These terms constitute the entire agreement between you and us regarding the Service.</p>

					<h5>13.2 Severability</h5>
					<p>If any provision is found unenforceable, the remaining provisions remain in effect.</p>

					<h5>13.3 Updates</h5>
					<p>We may update these terms periodically. Continued use constitutes acceptance of changes.</p>

					<h5>13.4 Contact</h5>
					<p>For questions about these terms, please contact us through the application.</p>
				</div>
			</Modal.Body>
			<Modal.Footer>
				<Button variant="primary" onClick={onHide}>
					Close
				</Button>
			</Modal.Footer>
		</Modal>
	);
}

export default TermsAndConditions;