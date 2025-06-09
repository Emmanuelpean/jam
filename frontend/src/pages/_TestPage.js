import React, { useState } from "react";
import { Button, Card, Row, Col } from "react-bootstrap";
import GenericModal from "../components/GenericModal";

const TestAlertsPage = () => {
	const [currentAlert, setCurrentAlert] = useState(null);

	const hideAlert = () => setCurrentAlert(null);

	const alertExamples = [
		{
			title: "Success Alert",
			description: "Simple success message",
			config: {
				show: true,
				mode: "alert",
				title: "Success!",
				alertType: "success",
				alertMessage: "Your operation completed successfully!",
				confirmText: "Great!",
				onHide: hideAlert,
			},
		},
		{
			title: "Error Alert",
			description: "Error message with details",
			config: {
				show: true,
				mode: "alert",
				title: "Error Occurred",
				alertType: "error",
				alertMessage: "Something went wrong. Please try again later.",
				confirmText: "OK",
				onHide: hideAlert,
			},
		},
		{
			title: "Warning Alert",
			description: "Warning with custom icon",
			config: {
				show: true,
				mode: "alert",
				title: "Warning",
				alertType: "warning",
				alertMessage: "This action may have unintended consequences. Please review your settings.",
				confirmText: "Understood",
				alertIcon: "bi-exclamation-diamond-fill",
				onHide: hideAlert,
			},
		},
		{
			title: "Info Alert",
			description: "Information with cancel option",
			config: {
				show: true,
				mode: "alert",
				title: "Information",
				alertType: "info",
				alertMessage: "Here's some helpful information about the current feature.",
				confirmText: "Got it",
				cancelText: "Dismiss",
				showCancel: true,
				size: "md",
				onHide: hideAlert,
			},
		},
		{
			title: "Delete Confirmation",
			description: "Destructive action confirmation",
			config: {
				show: true,
				mode: "confirmation",
				title: "Delete Item",
				confirmationMessage: "Are you sure you want to delete this item? This action cannot be undone.",
				confirmText: "Delete",
				cancelText: "Cancel",
				confirmVariant: "danger",
				onConfirm: () => {
					console.log("Item deleted!");
					hideAlert();
				},
				onHide: hideAlert,
			},
		},
		{
			title: "Save Changes Confirmation",
			description: "Save confirmation with details",
			config: {
				show: true,
				mode: "confirmation",
				title: "Save Changes",
				confirmationMessage: "You have unsaved changes. Would you like to save them before continuing?",
				confirmText: "Save",
				cancelText: "Discard",
				confirmVariant: "primary",
				onConfirm: () => {
					console.log("Changes saved!");
					hideAlert();
				},
				onHide: hideAlert,
			},
		},
		{
			title: "Large Alert with Custom Content",
			description: "Alert with additional custom content",
			config: {
				show: true,
				mode: "alert",
				title: "System Update",
				alertType: "info",
				alertMessage: "A new system update is available with the following improvements:",
				size: "lg",
				customContent: (
					<div className="mt-3">
						<ul className="list-group list-group-flush">
							<li className="list-group-item">🚀 Improved performance</li>
							<li className="list-group-item">🛡️ Enhanced security</li>
							<li className="list-group-item">🎨 Updated UI components</li>
							<li className="list-group-item">🐛 Bug fixes and stability improvements</li>
						</ul>
						<div className="alert alert-warning mt-3">
							<small>
								<strong>Note:</strong> The update will require a system restart.
							</small>
						</div>
					</div>
				),
				confirmText: "Update Now",
				cancelText: "Later",
				showCancel: true,
				onHide: hideAlert,
			},
		},
		{
			title: "Rich Content Alert",
			description: "Alert with JSX content instead of string",
			config: {
				show: true,
				mode: "alert",
				title: "Welcome!",
				alertType: "success",
				alertMessage: (
					<div>
						<p className="mb-3">
							<strong>Welcome to the application!</strong>
						</p>
						<p className="mb-2">Here are some quick tips to get started:</p>
						<div className="d-flex align-items-center mb-2">
							<i className="bi bi-check-circle-fill text-success me-2"></i>
							<span>Complete your profile setup</span>
						</div>
						<div className="d-flex align-items-center mb-2">
							<i className="bi bi-check-circle-fill text-success me-2"></i>
							<span>Explore the main features</span>
						</div>
						<div className="d-flex align-items-center">
							<i className="bi bi-check-circle-fill text-success me-2"></i>
							<span>Join our community forum</span>
						</div>
					</div>
				),
				confirmText: "Let's Start!",
				size: "md",
				onHide: hideAlert,
			},
		},
		{
			title: "Custom Footer Alert",
			description: "Alert with completely custom footer",
			config: {
				show: true,
				mode: "alert",
				title: "Custom Actions",
				alertType: "info",
				alertMessage: "This alert demonstrates custom footer buttons with different actions.",
				customFooter: (
					<div className="modal-footer justify-content-between">
						<Button variant="outline-secondary" onClick={hideAlert} size="sm">
							<i className="bi bi-arrow-left me-1"></i>
							Back
						</Button>
						<div>
							<Button
								variant="outline-primary"
								onClick={() => {
									console.log("Help clicked");
									hideAlert();
								}}
								size="sm"
								className="me-2"
							>
								<i className="bi bi-question-circle me-1"></i>
								Help
							</Button>
							<Button
								variant="primary"
								onClick={() => {
									console.log("Continue clicked");
									hideAlert();
								}}
								size="sm"
							>
								Continue
								<i className="bi bi-arrow-right ms-1"></i>
							</Button>
						</div>
					</div>
				),
				onHide: hideAlert,
			},
		},
		{
			title: "Small Confirmation",
			description: "Compact confirmation dialog",
			config: {
				show: true,
				mode: "confirmation",
				title: "Logout",
				confirmationMessage: "Are you sure you want to logout?",
				confirmText: "Logout",
				cancelText: "Stay",
				confirmVariant: "outline-danger",
				size: "sm",
				onConfirm: () => {
					console.log("User logged out");
					hideAlert();
				},
				onHide: hideAlert,
			},
		},
	];

	const showAlert = (config) => {
		setCurrentAlert(config);
	};

	return (
		<div className="container my-4">
			<h2 className="mb-4">Alert Modal Examples</h2>
			<p className="text-muted mb-4">
				Click on any button below to see different variations of alert modals using the GenericModal component.
			</p>

			<Row>
				{alertExamples.map((example, index) => (
					<Col key={index} md={6} lg={4} className="mb-3">
						<Card className="h-100">
							<Card.Body className="d-flex flex-column">
								<Card.Title className="h6">{example.title}</Card.Title>
								<Card.Text className="text-muted small flex-grow-1">{example.description}</Card.Text>
								<Button
									variant="outline-primary"
									size="sm"
									onClick={() => showAlert(example.config)}
									className="mt-auto"
								>
									Show Alert
								</Button>
							</Card.Body>
						</Card>
					</Col>
				))}
			</Row>

			{/* Render the current alert */}
			{currentAlert && <GenericModal {...currentAlert} />}

			{/* Additional demo section */}
			<div className="mt-5 pt-4 border-top">
				<h4>Quick Actions</h4>
				<div className="d-flex gap-2 flex-wrap">
					<Button
						variant="success"
						onClick={() =>
							showAlert({
								show: true,
								mode: "alert",
								title: "Success",
								alertType: "success",
								alertMessage: "Operation completed successfully!",
								confirmText: "OK",
								size: "sm",
								onHide: hideAlert,
							})
						}
					>
						Quick Success
					</Button>
					<Button
						variant="danger"
						onClick={() =>
							showAlert({
								show: true,
								mode: "confirmation",
								title: "Confirm Action",
								confirmationMessage: "This is a quick confirmation. Proceed?",
								confirmText: "Yes",
								cancelText: "No",
								confirmVariant: "danger",
								size: "sm",
								onConfirm: () => {
									console.log("Confirmed!");
									hideAlert();
								},
								onHide: hideAlert,
							})
						}
					>
						Quick Confirm
					</Button>
					<Button
						variant="warning"
						onClick={() =>
							showAlert({
								show: true,
								mode: "alert",
								title: "Warning",
								alertType: "warning",
								alertMessage: "This is a warning message!",
								confirmText: "Understood",
								size: "sm",
								onHide: hideAlert,
							})
						}
					>
						Quick Warning
					</Button>
				</div>
			</div>
		</div>
	);
};

export default TestAlertsPage;
