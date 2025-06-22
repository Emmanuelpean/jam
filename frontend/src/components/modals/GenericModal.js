import React, { useEffect, useRef, useState } from "react";
import { Alert, Button, Form, Modal, Spinner } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import "./GenericModal.css";
import { renderFieldValue, renderFunctions } from "../rendering/Renders";
import { renderInputField, renderInputFieldGroup } from "../rendering/WidgetRenders";
import { api } from "../../services/api";

const DEFAULT_ICONS = {
	form: "bi bi-pencil",
	view: "bi bi-eye",
	confirmation: "bi bi-exclamation-triangle",
	custom: "",
};

const DEFAULT_ALERT_ICONS = {
	success: "bi-check-circle-fill",
	warning: "bi-exclamation-triangle-fill",
	error: "bi-x-circle-fill",
	info: "bi-info-circle-fill",
};

const GenericModal = ({
	// Basic modal props
	show, // Boolean - Controls modal visibility
	onHide, // Function - Called when modal should be closed
	title, // String - Modal title text
	size = "lg", // String - Modal size: "sm", "md", "lg", "xl"
	centered = true, // Boolean - Whether to center modal vertically

	// Modal mode
	mode = "form", // String - Modal type: 'form', 'view', 'alert', 'confirmation', 'custom'

	// Form mode props
	fields = [], // Array - Field definitions or field groups for form mode
	initialData = {}, // Object - Initial form data
	endpoint, // String - API endpoint for form submission
	onSuccess, // Function - Called on successful form submission
	validationRules = {}, // Object - Custom validation rules for fields
	customValidation = null, // Function - Custom validation function
	transformFormData = null, // Function - Transform form data before submission
	isEdit = false, // Boolean - Whether form is in edit mode
	customFieldComponents = {},
	customSubmitHandler = null,
	onFormDataChange = null, // Function - Called when form data changes

	// View mode props
	data = null, // Object - Data to display in view mode
	viewFields = [], // Array - Field definitions for view mode display
	showSystemFields = true, // Boolean - Whether to show created/modified dates

	// Alert mode props
	alertType = "info", // String - Alert type: 'info', 'success', 'warning', 'error'
	alertMessage, // String|React.Node - Message to display in alert mode
	alertIcon = null, // String - Custom icon class for alert
	confirmText = "OK", // String - Text for confirm button
	cancelText = "Cancel", // String - Text for cancel button
	showCancel = false, // Boolean - Whether to show cancel button in alert mode

	// Confirmation mode props
	confirmationMessage = "Are you sure you want to proceed?", // String - Message for confirmation dialog
	onConfirm = null, // Function - Called when user confirms action
	confirmVariant = "danger", // String - Bootstrap variant for confirm button

	// Custom mode props
	customContent = null, // React.Node - Custom content for modal body

	// Advanced customization
	headerClassName = "", // String - Additional CSS classes for header
	bodyClassName = "", // String - Additional CSS classes for body
}) => {
	const { token } = useAuth();
	const [formData, setFormData] = useState(initialData);
	const [submitting, setSubmitting] = useState(false);
	const [errors, setErrors] = useState({});
	const previousShow = useRef(show);

	// Reset form data only when modal transitions from closed to open
	useEffect(() => {
		if (show && !previousShow.current && mode === "form") {
			setFormData({ ...initialData });
			setErrors({});
		}
		previousShow.current = show;
	}, [show, initialData, mode]);

	// Notify parent component when form data changes
	useEffect(() => {
		if (onFormDataChange && mode === "form") {
			onFormDataChange(formData);
		}
	}, [formData, onFormDataChange, mode]);

	// Handle modal hide
	const handleHide = () => {
		if (mode === "form") {
			setFormData({ ...initialData });
			setErrors({});
			setSubmitting(false);
		}
		onHide();
	};

	// Form handling
	const handleChange = (e) => {
		const { name, value, type, checked } = e.target;

		// Handle different input types
		let newValue;
		if (type === "checkbox") {
			newValue = checked;
		} else if (type === "file") {
			newValue = value; // For file inputs, value is already the File object
		} else {
			newValue = value;
		}

		setFormData((prev) => ({
			...prev,
			[name]: newValue,
		}));

		if (errors[name]) {
			setErrors((prev) => ({ ...prev, [name]: "" }));
		}
	};

	const handleSelectChange = (selectedOption, { name }) => {
		setFormData((prev) => ({
			...prev,
			[name]: selectedOption ? selectedOption.value : "",
		}));

		if (errors[name]) {
			setErrors((prev) => ({ ...prev, [name]: "" }));
		}
	};

	const extractAllFields = (fieldsArray) => {
		const allFields = [];

		fieldsArray.forEach((item) => {
			if (Array.isArray(item)) {
				allFields.push(...item);
			} else if (item.name) {
				allFields.push(item);
			}
		});

		return allFields;
	};

	// Form validation
	const validateForm = () => {
		const newErrors = {};
		const allFields = extractAllFields(fields);

		allFields.forEach((field) => {
			if (field.required && !formData[field.name]) {
				newErrors[field.name] = `${field.label} is required`;
			}

			if (validationRules[field.name]) {
				const validation = validationRules[field.name](formData[field.name], formData);
				if (!validation.isValid) {
					newErrors[field.name] = validation.message;
				}
			}
		});

		if (customValidation) {
			const customErrors = customValidation(formData);
			Object.assign(newErrors, customErrors);
		}

		return newErrors;
	};

	const handleSubmit = async (e) => {
		e.preventDefault();

		if (mode === "alert") {
			if (onSuccess) onSuccess();
			handleHide();
			return;
		}

		if (mode === "confirmation") {
			if (onConfirm) onConfirm();
			handleHide();
			return;
		}

		if (mode !== "form") return;

		const validationErrors = validateForm();
		if (Object.keys(validationErrors).length > 0) {
			setErrors(validationErrors);
			return;
		}

		setSubmitting(true);
		setErrors({});

		try {
			// If custom submit handler is provided, use it
			if (customSubmitHandler) {
				await customSubmitHandler(e.target, async (processedData) => {
					// This callback will be called by the custom handler with processed data
					const dataToSubmit = transformFormData ? transformFormData(processedData) : processedData;

					let result;
					if (isEdit) {
						result = await api.put(`${endpoint}/${initialData.id}`, dataToSubmit, token);
					} else {
						result = await api.post(`${endpoint}/`, dataToSubmit, token);
					}

					if (onSuccess) onSuccess(result);
					handleHide();
				});
			} else {
				// Default submission logic for forms without custom handling
				const dataToSubmit = transformFormData ? transformFormData(formData) : formData;

				let result;
				if (isEdit) {
					result = await api.put(`${endpoint}/${initialData.id}`, dataToSubmit, token);
				} else {
					result = await api.post(`${endpoint}/`, dataToSubmit, token);
				}

				if (onSuccess) onSuccess(result);
				handleHide();
			}
		} catch (err) {
			console.error(`Error ${isEdit ? "updating" : "creating"} ${title.toLowerCase()}:`, err);

			// Use the error message from the API response if available
			const errorMessage =
				err.data?.detail ||
				err.message ||
				`Failed to ${isEdit ? "update" : "create"} ${title.toLowerCase()}. Please try again.`;

			setErrors({
				submit: errorMessage,
			});
		} finally {
			setSubmitting(false);
		}
	};

	// Modal header
	const renderHeader = () => {
		// Icon
		let icon;
		if (alertIcon) {
			icon = alertIcon;
		} else if (mode === "alert") {
			icon = DEFAULT_ALERT_ICONS[alertType];
		} else {
			icon = DEFAULT_ICONS[mode];
		}

		// Title
		let text = title;
		if (mode === "view") {
			text = `${title} Details`;
		} else if (mode === "form") {
			if (isEdit) {
				text = `Edit ${title}`;
			} else {
				text = `Add New ${title}`;
			}
		}

		return (
			<Modal.Header closeButton className={headerClassName}>
				<Modal.Title>
					{icon && <i className={`${icon} me-2`} style={{ fontSize: "1.05em" }} />}
					{text}
				</Modal.Title>
			</Modal.Header>
		);
	};

	// Render individual field (for simple fields)
	const renderFormGroup = (field) => (
		<Form.Group key={field.name} className="mb-3">
			<Form.Label>
				{field.label}
				{field.required && <span className="text-danger">*</span>}
			</Form.Label>
			{renderInputField(field, formData, handleChange, errors, handleSelectChange, customFieldComponents)}
			{errors[field.name] && <div className="invalid-feedback d-block">{errors[field.name]}</div>}
		</Form.Group>
	);

	// Render modal body
	const renderBody = () => {
		if (mode === "form") {
			return (
				<div>
					{errors.submit && <Alert variant="danger">{errors.submit}</Alert>}
					<div>
						{fields.map((item, index) => {
							// Type 1: Array of fields (render as row)
							if (Array.isArray(item)) {
								return renderInputFieldGroup({ fields: item }, formData, handleChange, errors, handleSelectChange, customFieldComponents);
							}

							// Type 2: Single field (has name property)
							if (item.name) {
								return (
									<Form.Group key={item.name} className="mb-3">
										{item.type !== "drag-drop" && (
											<Form.Label>
												{item.label}
												{item.required && <span className="text-danger">*</span>}
											</Form.Label>
										)}
										{renderInputField(item, formData, handleChange, errors, handleSelectChange, customFieldComponents)}
									</Form.Group>
								);
							}

							// Type 3: Custom object or legacy object with fields
							return renderInputFieldGroup(item, formData, handleChange, errors, handleSelectChange, customFieldComponents);
						})
						}
					</div>
					{customContent && <div className="mt-4">{customContent}</div>}
				</div>
			);
		} else if (mode === "view") {
			return (
				<div>
					<div className="row">
						{viewFields.map((field) => (
							<div key={field.name} className={field.type === "textarea" ? "col-12" : "col-md-6"}>
								<h6 className="mb-3 fw-bold">{field.label}</h6>
								<div className="mb-3">{renderFieldValue(field, data)}</div>
							</div>
						))}
					</div>
					<div className="mt-4">{customContent}</div>
					{showSystemFields && (
						<div className="row mt-3 pt-3 border-top">
							<div className="col-md-6">
								<h6>Date Added</h6>
								<div className="mb-3">{renderFunctions.createdDate(data, true)}</div>
							</div>

							<div className="col-md-6">
								<h6>Last Updated</h6>
								<div className="mb-3">{renderFunctions.modifiedDate(data, true)}</div>
							</div>
						</div>
					)}
				</div>
			);
		} else if (mode === "alert") {
			return (
				<div>
					<div className="text-center py-3">
						{typeof alertMessage === "string" ? <p className="mb-0">{alertMessage}</p> : alertMessage}
					</div>
					<div className="mt-4">{customContent}</div>
				</div>
			);
		} else if (mode === "confirmation") {
			return (
				<div>
					<p className="mb-0">{confirmationMessage}</p>
					<div className="mt-4">{customContent}</div>
				</div>
			);
		} else {
			return customContent;
		}
	};

	// Render modal footer
	const renderFooter = () => {
		if (mode === "form") {
			return (
				<Modal.Footer>
					<div className={"modal-buttons-container"}>
						<Button variant="secondary" onClick={handleHide}>
							Cancel
						</Button>
						<Button variant="primary" type="submit" disabled={submitting}>
							{submitting ? (
								<>
									<Spinner animation="border" size="sm" className="me-2" />
									{isEdit ? "Updating..." : "Saving..."}
								</>
							) : (
								(isEdit ? "Update" : "Save") + ` ${title}`
							)}
						</Button>
					</div>
				</Modal.Footer>
			);
		} else if (mode === "view") {
			return (
				<Modal.Footer>
					<div className="w-100">
						<Button variant="primary" onClick={handleHide} className="w-100">
							Close
						</Button>
					</div>
				</Modal.Footer>
			);
		} else if (mode === "alert") {
			return (
				<Modal.Footer className={"modal-buttons-container"}>
					{showCancel && (
						<Button
							variant="secondary"
							onClick={handleHide}
							size="lg"
							style={{ minWidth: "100px" }}
							className="me-2"
						>
							{cancelText}
						</Button>
					)}
					<Button onClick={handleSubmit} size="lg" style={{ minWidth: "100px" }}>
						{confirmText}
					</Button>
				</Modal.Footer>
			);
		} else if (mode === "confirmation") {
			return (
				<Modal.Footer className={"modal-buttons-container"}>
					<Button variant="secondary" onClick={handleHide}>
						{cancelText}
					</Button>
					<Button variant={confirmVariant} onClick={handleSubmit}>
						{confirmText}
					</Button>
				</Modal.Footer>
			);
		} else {
			return null;
		}
	};

	const modalContent = (
		<>
			{renderHeader()}
			{<Modal.Body className={bodyClassName}>{renderBody()}</Modal.Body>}
			{renderFooter()}
		</>
	);

	return (
		<Modal show={show} onHide={handleHide} size={size} centered={centered} backdrop={true} keyboard={true}>
			{mode === "form" ? <Form onSubmit={handleSubmit}>{modalContent}</Form> : modalContent}
		</Modal>
	);
};

export default GenericModal;
