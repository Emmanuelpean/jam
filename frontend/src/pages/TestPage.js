import React, { useState } from "react";
import { Container, Row, Col, Card, Button, Modal, Form, Alert } from "react-bootstrap";
import Select from "react-select";
import ThemeToggle from "../components/ui/ThemeToggle";
import GenericModal from "../components/GenericModal";
import useGenericAlert from "../hooks/useGenericAlert";
import "../index.css";

const StyleShowcase = () => {
	const [showModal, setShowModal] = useState(false);
	const [formData, setFormData] = useState({
		textInput: "",
		emailInput: "",
		passwordInput: "",
		urlInput: "",
		numberInput: "",
		dateInput: "",
		textareaInput: "",
		selectInput: "",
		checkboxInput: false,
		toggleInput: false,
		notificationToggle: true,
		darkModeToggle: false,
		rangeInput: 3,
		reactSelectInput: "",
	});
	const [errors, setErrors] = useState({});
	const [showErrorStates, setShowErrorStates] = useState(false);

	// Alert modal state using new hook
	const { alertState, showAlert, hideAlert } = useGenericAlert();

	const handleChange = (e) => {
		const { name, value, type, checked } = e.target;
		setFormData((prev) => ({
			...prev,
			[name]: type === "checkbox" ? checked : value,
		}));
	};

	const handleSelectChange = (selectedOption) => {
		setFormData((prev) => ({
			...prev,
			reactSelectInput: selectedOption ? selectedOption.value : "",
		}));
	};

	const toggleErrorStates = () => {
		if (!showErrorStates) {
			setErrors({
				textInput: "This field is required",
				emailInput: "Please enter a valid email address",
				numberInput: "Value must be between 1 and 100",
				selectInput: "Please select an option",
			});
		} else {
			setErrors({});
		}
		setShowErrorStates(!showErrorStates);
	};

	// Alert modal handlers
	const handleInfoAlert = () => {
		showAlert({
			title: "Information",
			message: "This is an informational alert. It provides helpful information to the user.",
			type: "info",
			confirmText: "Got it!",
			icon: "ℹ️",
		});
	};

	const handleSuccessAlert = () => {
		showAlert({
			title: "Success!",
			message: "Your operation was completed successfully. All changes have been saved.",
			type: "success",
			confirmText: "Awesome!",
			icon: "✅",
		});
	};

	const handleWarningAlert = () => {
		showAlert({
			title: "Warning",
			message: "Please be careful! This action might have unexpected consequences. Do you want to continue?",
			type: "warning",
			confirmText: "I understand",
			icon: "⚠️",
		});
	};

	const handleErrorAlert = () => {
		showAlert({
			title: "Error Occurred",
			message: "Something went wrong while processing your request. Please try again later or contact support.",
			type: "error",
			confirmText: "Close",
			icon: "❌",
		});
	};

	const handleCustomAlert = () => {
		showAlert({
			title: "Custom Alert",
			message: (
				<div>
					<p>This is a custom alert with HTML content!</p>
					<ul>
						<li>You can include lists</li>
						<li>Multiple paragraphs</li>
						<li>And other formatting</li>
					</ul>
					<p className="text-muted mb-0">
						<small>This demonstrates the flexibility of the alert system.</small>
					</p>
				</div>
			),
			type: "info",
			icon: "🚀",
			size: "lg",
			confirmText: "Amazing!",
		});
	};

	const handleLargeAlert = () => {
		showAlert({
			title: "Large Alert Modal",
			message:
				"This is a large-sized alert modal that provides more space for content. It's useful when you need to display more detailed information or longer messages that require better readability and formatting.",
			type: "info",
			size: "lg",
			confirmText: "Perfect!",
			icon: "📏",
		});
	};

	const handleSmallAlert = () => {
		showAlert({
			title: "Quick Note",
			message: "Small alert for brief messages.",
			type: "warning",
			size: "sm",
			confirmText: "OK",
			icon: "💡",
		});
	};

	const selectOptions = [
		{ value: "option1", label: "Option 1" },
		{ value: "option2", label: "Option 2" },
		{ value: "option3", label: "Option 3" },
		{ value: "option4", label: "Very Long Option Name That Might Wrap" },
		{ value: "option5", label: "Another Option" },
	];

	const customSelectStyles = {
		control: (provided, state) => ({
			...provided,
			borderColor: errors.reactSelectInput ? "#dc3545" : "#dee2e6",
			boxShadow: state.isFocused ? "0 0 0 0.2rem rgba(13, 110, 253, 0.25)" : "none",
			"&:hover": {
				borderColor: errors.reactSelectInput ? "#dc3545" : "#86b7fe",
			},
			minHeight: "48px",
		}),
		valueContainer: (provided) => ({
			...provided,
			padding: "0.375rem 0.75rem",
		}),
		input: (provided) => ({
			...provided,
			margin: 0,
			padding: 0,
			color: "#212529",
		}),
		placeholder: (provided) => ({
			...provided,
			color: "#6c757d",
			fontStyle: "italic",
		}),
		singleValue: (provided) => ({
			...provided,
			color: "#212529",
		}),
		menu: (provided) => ({
			...provided,
			zIndex: 9999,
		}),
	};

	return (
		<Container fluid className="py-4">
			<Row className="justify-content-center">
				<Col lg={10}>
					<Card className="shadow-lg">
						<Card.Header className="bg-primary text-white d-flex justify-content-between align-items-center">
							<div>
								<h2 className="mb-0">Form Styles Showcase</h2>
								<p className="mb-0 mt-2 opacity-75">
									Comprehensive demonstration of all form styling components
								</p>
							</div>
							<ThemeToggle />
						</Card.Header>
						<Card.Body className="p-4">
							{/* Control Buttons */}
							<Row className="mb-4">
								<Col>
									<div className="d-flex gap-3 flex-wrap">
										<Button variant="primary" onClick={() => setShowModal(true)}>
											Open Modal Example
										</Button>
										<Button
											variant={showErrorStates ? "success" : "warning"}
											onClick={toggleErrorStates}
										>
											{showErrorStates ? "Hide" : "Show"} Error States
										</Button>
										<Button variant="secondary" disabled>
											Disabled Button
										</Button>
									</div>
								</Col>
							</Row>

							{/* Alert Modal Examples */}
							<Row className="mb-4">
								<Col>
									<h4 className="mb-3">Alert Modal Examples</h4>
									<div className="d-flex gap-2 flex-wrap mb-3">
										<Button variant="info" onClick={handleInfoAlert}>
											Info Alert
										</Button>
										<Button variant="success" onClick={handleSuccessAlert}>
											Success Alert
										</Button>
										<Button variant="warning" onClick={handleWarningAlert}>
											Warning Alert
										</Button>
										<Button variant="danger" onClick={handleErrorAlert}>
											Error Alert
										</Button>
										<Button variant="primary" onClick={handleCustomAlert}>
											Custom Alert
										</Button>
									</div>
									<div className="d-flex gap-2 flex-wrap">
										<Button variant="outline-primary" onClick={handleLargeAlert}>
											Large Alert
										</Button>
										<Button variant="outline-secondary" onClick={handleSmallAlert}>
											Small Alert
										</Button>
									</div>
								</Col>
							</Row>

							{/* Alert Examples */}
							<Row className="mb-4">
								<Col>
									<h4 className="mb-3">Bootstrap Alert Components</h4>
									<Alert variant="primary" className="mb-2">
										<Alert.Heading>Primary Alert</Alert.Heading>
										This is a primary alert with additional content.
									</Alert>
									<Alert variant="success" className="mb-2">
										<strong>Success!</strong> Your action was completed successfully.
									</Alert>
									<Alert variant="warning" className="mb-2">
										<strong>Warning!</strong> Please check your input before proceeding.
									</Alert>
									<Alert variant="danger" className="mb-2">
										<strong>Error!</strong> Something went wrong. Please try again.
									</Alert>
									<Alert variant="info" className="mb-2">
										<strong>Info:</strong> Here's some helpful information for you.
									</Alert>
								</Col>
							</Row>

							{/* Form Elements */}
							<Row>
								<Col md={6}>
									<h4 className="mb-3">Text Inputs</h4>

									<Form.Group className="mb-3">
										<Form.Label>Text Input</Form.Label>
										<Form.Control
											type="text"
											name="textInput"
											value={formData.textInput}
											onChange={handleChange}
											placeholder="Enter some text"
											isInvalid={!!errors.textInput}
										/>
										{errors.textInput && (
											<Form.Control.Feedback type="invalid">
												{errors.textInput}
											</Form.Control.Feedback>
										)}
									</Form.Group>

									<Form.Group className="mb-3">
										<Form.Label>Email Input</Form.Label>
										<Form.Control
											type="email"
											name="emailInput"
											value={formData.emailInput}
											onChange={handleChange}
											placeholder="Enter your email"
											isInvalid={!!errors.emailInput}
										/>
										{errors.emailInput && (
											<Form.Control.Feedback type="invalid">
												{errors.emailInput}
											</Form.Control.Feedback>
										)}
									</Form.Group>

									<Form.Group className="mb-3">
										<Form.Label>Password Input</Form.Label>
										<Form.Control
											type="password"
											name="passwordInput"
											value={formData.passwordInput}
											onChange={handleChange}
											placeholder="Enter your password"
										/>
									</Form.Group>

									<Form.Group className="mb-3">
										<Form.Label>URL Input</Form.Label>
										<Form.Control
											type="url"
											name="urlInput"
											value={formData.urlInput}
											onChange={handleChange}
											placeholder="https://example.com"
										/>
									</Form.Group>

									<Form.Group className="mb-3">
										<Form.Label>Number Input</Form.Label>
										<Form.Control
											type="number"
											name="numberInput"
											value={formData.numberInput}
											onChange={handleChange}
											placeholder="Enter a number"
											min="1"
											max="100"
											isInvalid={!!errors.numberInput}
										/>
										{errors.numberInput && (
											<Form.Control.Feedback type="invalid">
												{errors.numberInput}
											</Form.Control.Feedback>
										)}
									</Form.Group>

									<Form.Group className="mb-3">
										<Form.Label>Date Input</Form.Label>
										<Form.Control
											type="date"
											name="dateInput"
											value={formData.dateInput}
											onChange={handleChange}
										/>
									</Form.Group>
								</Col>

								<Col md={6}>
									<h4 className="mb-3">Other Form Controls</h4>

									<Form.Group className="mb-3">
										<Form.Label>Textarea</Form.Label>
										<Form.Control
											as="textarea"
											rows={3}
											name="textareaInput"
											value={formData.textareaInput}
											onChange={handleChange}
											placeholder="Enter multiple lines of text"
										/>
									</Form.Group>

									<Form.Group className="mb-3">
										<Form.Label>Select Dropdown</Form.Label>
										<Form.Select
											name="selectInput"
											value={formData.selectInput}
											onChange={handleChange}
											isInvalid={!!errors.selectInput}
										>
											<option value="">Choose an option</option>
											<option value="option1">Option 1</option>
											<option value="option2">Option 2</option>
											<option value="option3">Option 3</option>
										</Form.Select>
										{errors.selectInput && (
											<Form.Control.Feedback type="invalid">
												{errors.selectInput}
											</Form.Control.Feedback>
										)}
									</Form.Group>

									<Form.Group className="mb-3">
										<Form.Label>React Select</Form.Label>
										<Select
											name="reactSelectInput"
											value={selectOptions.find(
												(option) => option.value === formData.reactSelectInput,
											)}
											onChange={handleSelectChange}
											options={selectOptions}
											placeholder="Choose an option..."
											isSearchable
											isClearable
											styles={customSelectStyles}
											menuPortalTarget={document.body}
										/>
										{errors.reactSelectInput && (
											<div className="text-danger small mt-1">{errors.reactSelectInput}</div>
										)}
									</Form.Group>

									<Form.Group className="mb-3">
										<Form.Label>Range Input</Form.Label>
										<Form.Range
											name="rangeInput"
											value={formData.rangeInput}
											onChange={handleChange}
											min="1"
											max="5"
										/>
										<div className="text-muted small">Value: {formData.rangeInput}</div>
									</Form.Group>

									<h5 className="mb-3">Checkboxes & Switches</h5>

									<Form.Group className="mb-3">
										<Form.Check
											type="checkbox"
											name="checkboxInput"
											checked={formData.checkboxInput}
											onChange={handleChange}
											label="Regular Checkbox"
										/>
									</Form.Group>

									<Form.Group className="mb-3">
										<Form.Check
											type="switch"
											name="toggleInput"
											checked={formData.toggleInput}
											onChange={handleChange}
											label="Toggle Switch"
										/>
									</Form.Group>

									<Form.Group className="mb-3">
										<Form.Check
											type="switch"
											name="notificationToggle"
											checked={formData.notificationToggle}
											onChange={handleChange}
											label="Enable Notifications"
										/>
									</Form.Group>

									<Form.Group className="mb-3">
										<Form.Check
											type="switch"
											name="darkModeToggle"
											checked={formData.darkModeToggle}
											onChange={handleChange}
											label="Dark Mode"
										/>
									</Form.Group>
								</Col>
							</Row>
						</Card.Body>
					</Card>
				</Col>
			</Row>

			{/* Test Modal */}
			<Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
				<Modal.Header closeButton>
					<Modal.Title>Test Modal</Modal.Title>
				</Modal.Header>
				<Modal.Body>
					<p>This is a test modal to demonstrate modal styling in different themes.</p>
					<Form>
						<Form.Group className="mb-3">
							<Form.Label>Sample Input in Modal</Form.Label>
							<Form.Control type="text" placeholder="Type something here..." />
						</Form.Group>
						<Form.Group className="mb-3">
							<Form.Check type="switch" label="Sample Switch in Modal" />
						</Form.Group>
					</Form>
				</Modal.Body>
				<Modal.Footer>
					<Button variant="secondary" onClick={() => setShowModal(false)}>
						Close
					</Button>
					<Button variant="primary">Save Changes</Button>
				</Modal.Footer>
			</Modal>

			{/* Alert Modal using GenericModal */}
			<GenericModal
				show={alertState.show}
				onHide={hideAlert}
				mode="alert"
				title={alertState.title}
				alertMessage={alertState.message}
				alertType={alertState.type}
				confirmText={alertState.confirmText}
				alertIcon={alertState.icon}
				size={alertState.size}
				onSuccess={alertState.onSuccess}
			/>
		</Container>
	);
};

export default StyleShowcase;
