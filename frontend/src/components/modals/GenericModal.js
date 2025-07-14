import React, { useEffect, useRef, useState } from "react";
import { Alert, Button, Form, Modal, Spinner } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import "./GenericModal.css";
import { renderFieldValue } from "../rendering/Renders";
import { renderInputField } from "../rendering/WidgetRenders";
import { api } from "../../services/api";
import { viewFields as viewFieldsLib } from "../rendering/ViewRenders";

const DEFAULT_ICONS = {
	formview: "bi bi-eye",
	confirmation: "bi bi-exclamation-triangle",
	alert: "bi bi-info-circle",
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
	mode = "formview", // String - Modal type: 'formview', 'alert', 'confirmation', 'custom'
	submode = "view", // String - Submode for formview: 'view', 'edit', 'add'
	fields = {}, // Field definitions or field groups (or object with form/view keys for formview mode)

	// FormView mode props
	data = null, // Object - Data to display/edit
	endpoint, // String - API endpoint for form submission
	onSuccess, // Function - Called on successful form submission
	validation = null,
	transformFormData = null, // Function - Transform form data before submission
	customSubmitHandler = null,
	onFormDataChange = null, // Function - Called when form data changes
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
}) => {
	const { token } = useAuth();
	const [formData, setFormData] = useState(data || {});
	const [submitting, setSubmitting] = useState(false);
	const [errors, setErrors] = useState({});
	const [isEditing, setIsEditing] = useState(false); // State for formview mode
	const [isTransitioning, setIsTransitioning] = useState(false); // Animation state
	const [contentHeight, setContentHeight] = useState("auto"); // Height for smooth transitions
	const previousShow = useRef(show);
	const modalBodyRef = useRef(null);
	const viewContentRef = useRef(null);
	const formContentRef = useRef(null);

	// Reset form data and editing state when modal opens
	useEffect(() => {
		if (show && !previousShow.current) {
			if (mode === "formview") {
				// Handle different submodes
				if (submode === "add") {
					setFormData({});
					setIsEditing(true);
				} else if (submode === "edit") {
					setFormData({ ...data });
					setIsEditing(true);
				} else {
					// Default view submode
					setFormData({ ...data });
					setIsEditing(false);
				}
				setErrors({});
				setIsTransitioning(false);
				setContentHeight("auto");
			}
		}
		previousShow.current = show;
	}, [show, data, mode, submode]);

	// Notify parent component when form data changes
	useEffect(() => {
		if (onFormDataChange && mode === "formview" && isEditing) {
			onFormDataChange(formData);
		}
	}, [formData, onFormDataChange, mode, isEditing]);

	// Handle modal hide
	const handleHide = () => {
		if (mode === "formview") {
			if (submode === "add") {
				setFormData({});
			} else {
				setFormData({ ...data });
			}
			setErrors({});
			setSubmitting(false);
			setIsEditing(submode === "add" || submode === "edit");
			setIsTransitioning(false);
			setContentHeight("auto");
		}
		onHide();
	};

	// Measure content height from the hidden content
	const measureContentHeight = (targetMode) => {
		const targetRef = targetMode === "form" ? formContentRef : viewContentRef;
		if (targetRef.current) {
			return targetRef.current.scrollHeight;
		}
		return "auto";
	};

	// Handle edit button click (for formview mode) with smooth height animation
	const handleEdit = () => {
		if (isTransitioning) return;

		setIsTransitioning(true);

		// Get current and target heights
		const currentHeight = modalBodyRef.current?.scrollHeight || "auto";
		const targetHeight = measureContentHeight("form");

		// Set current height to prevent jumping
		setContentHeight(currentHeight + "px");

		// Small delay to allow height to be set
		setTimeout(() => {
			// Switch to edit mode
			setIsEditing(true);
			setFormData({ ...data });

			// Animate to new height
			setTimeout(() => {
				setContentHeight(targetHeight + "px");

				// Complete transition after animation
				setTimeout(() => {
					setIsTransitioning(false);
					setContentHeight("auto");
				}, 300);
			}, 0);
		}, 0);
	};

	// Handle cancel edit (for formview mode) with smooth height animation
	const handleCancelEdit = () => {
		if (isTransitioning) return;

		setIsTransitioning(true);

		// Get current and target heights
		const currentHeight = modalBodyRef.current?.scrollHeight || "auto";
		const targetHeight = measureContentHeight("view");

		// Set current height to prevent jumping
		setContentHeight(currentHeight + "px");

		// Small delay to allow height to be set
		setTimeout(() => {
			// Switch to view mode
			setIsEditing(false);
			setFormData({ ...data });
			setErrors({});

			// Animate to new height
			setTimeout(() => {
				setContentHeight(targetHeight + "px");

				// Complete transition after animation
				setTimeout(() => {
					setIsTransitioning(false);
					setContentHeight("auto");
				}, 300);
			}, 0);
		}, 0);
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
			} else if (item.name || item.key) {
				allFields.push(item);
			}
		});

		return allFields;
	};

	// Get current fields based on editing state
	const getCurrentFields = () => {
		if (mode === "formview") {
			if (isEditing) {
				return fields.form || fields;
			} else {
				return fields.view || fields;
			}
		}
		return fields;
	};

	// Shared field group rendering function
	const renderFieldGroup = (item, index, isFormMode = true) => {
		// Type 1: Array of fields or single field
		if (item.name || item.key) {
			item = [item];
		}
		if (Array.isArray(item)) {
			// Calculate column class based on number of fields
			const getColumnClass = (fieldCount) => {
				switch (fieldCount) {
					case 1:
						return "col-md-12";
					case 2:
						return "col-md-6";
					case 3:
						return "col-md-4";
					case 4:
						return "col-md-3";
					default:
						return "col-md-6";
				}
			};

			const columnClass = getColumnClass(item.length);

			return (
				<div key={index} className="row mb-3" style={{ paddingRight: "0.3rem", paddingLeft: "0.3rem" }}>
					{item.map((field) => (
						<div key={field.key + "_group"} className={columnClass}>
							{isFormMode ? (
								<Form.Group className="mb-3">
									{field.type !== "drag-drop" && field.type !== "table" && (
										<Form.Label>
											{field.label}
											{field.required && <span className="text-danger">*</span>}
										</Form.Label>
									)}
									{renderInputField(field, formData, handleChange, errors, handleSelectChange)}
								</Form.Group>
							) : (
								<div className="view-field">
									<h6 className="mb-2 fw-bold">{field.label}</h6>
									<div className="mb-3">{renderFieldValue(field, data)}</div>
								</div>
							)}
						</div>
					))}
				</div>
			);
		}
		return null;
	};

	// Render both view and form content for formview mode
	const renderFormViewContent = () => {
		const viewF = fields.view || fields;
		const formF = fields.form || fields;

		return (
			<>
				{/* Visible content */}
				<div className={`modal-content-visible ${isTransitioning ? "transitioning" : ""}`}>
					{isEditing ? (
						<div>
							{errors.submit && <Alert variant="danger">{errors.submit}</Alert>}
							<div>{formF.map((item, index) => renderFieldGroup(item, index, true))}</div>
						</div>
					) : (
						<div>
							<div>{viewF.map((item, index) => renderFieldGroup(item, index, false))}</div>
							{showSystemFields && (
								<div className="mt-3 pt-3 border-top">
									{renderFieldGroup(
										[viewFieldsLib.createdAt(), viewFieldsLib.modifiedAt()],
										"system-fields",
										false,
									)}
								</div>
							)}
						</div>
					)}
				</div>

				{/* Hidden content for measurement */}
				<div ref={viewContentRef} className="modal-content-hidden">
					<div>{viewF.map((item, index) => renderFieldGroup(item, index, false))}</div>
					{showSystemFields && (
						<div className="mt-3 pt-3 border-top">
							{renderFieldGroup(
								[viewFieldsLib.createdAt(), viewFieldsLib.modifiedAt()],
								"system-fields",
								false,
							)}
						</div>
					)}
				</div>
				<div ref={formContentRef} className="modal-content-hidden">
					{errors.submit && <Alert variant="danger">{errors.submit}</Alert>}
					<div>{formF.map((item, index) => renderFieldGroup(item, index, true))}</div>
				</div>
			</>
		);
	};

	// Form validation
	const validateForm = async () => {
		const newErrors = {};
		const currentFields = getCurrentFields();
		const allFields = extractAllFields(currentFields);

		// Required field validation
		allFields.forEach((field) => {
			if (field.required && !formData[field.name]) {
				newErrors[field.name] = `${field.label} is required`;
			}
		});

		if (validation) {
			if (typeof validation === "function") {
				// Check if validation function is async
				const customErrorsResult = validation(formData);

				// Handle both sync and async validation functions
				const customErrors =
					customErrorsResult instanceof Promise ? await customErrorsResult : customErrorsResult;

				Object.assign(newErrors, customErrors);
			} else if (typeof validation === "object") {
				// Object-based validation (like current validationRules)
				const validationPromises = Object.keys(validation).map(async (fieldName) => {
					const rule = validation[fieldName];
					const result = rule(formData[fieldName], formData);

					// Handle both sync and async validation rules
					const validationResult = result instanceof Promise ? await result : result;

					if (!validationResult.isValid) {
						return { fieldName, message: validationResult.message };
					}
					return null;
				});

				const validationResults = await Promise.all(validationPromises);
				validationResults.forEach((result) => {
					if (result) {
						newErrors[result.fieldName] = result.message;
					}
				});
			}
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

		if (mode === "formview" && !isEditing) return;
		if (mode !== "formview") return;

		// Add loading state for async validation
		setSubmitting(true);
		setErrors({});

		try {
			// Async validation
			const validationErrors = await validateForm();
			if (Object.keys(validationErrors).length > 0) {
				setErrors(validationErrors);
				setSubmitting(false);
				return;
			}

			// Continue with submission logic...
			const performSubmission = async (processedData) => {
				const dataToSubmit = transformFormData ? transformFormData(processedData) : processedData;

				let result;
				if (submode === "add") {
					result = await api.post(`${endpoint}/`, dataToSubmit, token);
				} else {
					const itemId = data?.id;
					result = await api.put(`${endpoint}/${itemId}`, dataToSubmit, token);
				}

				// Call success callback
				if (onSuccess) onSuccess(result);

				// Handle post-submission behavior
				if (submode === "add" || submode === "edit") {
					handleHide();
				} else {
					// Update data and return to view mode
					Object.assign(data, result);
					await handleCancelEdit();
				}
			};

			// Use custom handler if provided, otherwise use default form data
			if (customSubmitHandler) {
				await customSubmitHandler(e.target, performSubmission);
			} else {
				await performSubmission(formData);
			}
		} catch (err) {
			console.error(`Error ${submode === "add" ? "creating" : "updating"} ${title.toLowerCase()}:`, err);

			// Use the error message from the API response if available
			const errorMessage =
				err.data?.detail ||
				err.message ||
				`Failed to ${submode === "add" ? "create" : "update"} ${title.toLowerCase()}. Please try again.`;

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
		} else if (mode === "formview") {
			if (submode === "add") {
				icon = "bi bi-plus-circle";
			} else if (submode === "edit" || isEditing) {
				icon = "bi bi-pencil";
			} else {
				icon = "bi bi-eye";
			}
		} else {
			icon = DEFAULT_ICONS[mode];
		}

		// Title
		let text = title;
		if (mode === "formview") {
			if (submode === "add") {
				text = `Add New ${title}`;
			} else if (submode === "edit" || isEditing) {
				text = `Edit ${title}`;
			} else {
				text = `${title} Details`;
			}
		}

		return (
			<Modal.Header closeButton>
				<Modal.Title>
					{icon && <i className={`${icon} me-2`} style={{ fontSize: "1.05em" }} />}
					{text}
				</Modal.Title>
			</Modal.Header>
		);
	};

	// Render modal body
	const renderBody = () => {
		if (mode === "formview") {
			return (
				<div
					className="modal-content-container"
					style={{
						height: contentHeight,
						transition: contentHeight === "auto" ? "none" : "height 0.4s cubic-bezier(0.25, 0.8, 0.25, 1)",
					}}
				>
					{renderFormViewContent()}
				</div>
			);
		} else if (mode === "alert") {
			return (
				<div>
					<div className="text-center py-3">
						{typeof alertMessage === "string" ? <p className="mb-0">{alertMessage}</p> : alertMessage}
					</div>
				</div>
			);
		} else if (mode === "confirmation") {
			return (
				<div>
					<p className="mb-0">{confirmationMessage}</p>
				</div>
			);
		}
	};

	// Render modal footer
	const renderFooter = () => {
		if (mode === "formview") {
			if (isEditing) {
				if (submode === "add") {
					return (
						<Modal.Footer>
							<div className="d-flex flex-column w-100 gap-2">
								<div className="modal-buttons-container">
									<Button
										variant="secondary"
										onClick={handleHide}
										disabled={isTransitioning}
										id="cancel-button"
									>
										Cancel
									</Button>
									<Button
										variant="primary"
										type="submit"
										disabled={submitting || isTransitioning}
										id="confirm-button"
									>
										{submitting ? (
											<>
												<Spinner animation="border" size="sm" className="me-2" />
												Submitting...
											</>
										) : (
											"Confirm"
										)}
									</Button>
								</div>
							</div>
						</Modal.Footer>
					);
				} else {
					return (
						<Modal.Footer>
							<div className="d-flex flex-column w-100 gap-2">
								{/* First row: Delete and Confirm */}
								<div className="modal-buttons-container">
									<Button variant="danger" disabled={isTransitioning} id="delete-button">
										<i className="bi bi-trash me-2"></i>
										Delete
									</Button>

									<Button
										variant="primary"
										type="submit"
										disabled={submitting || isTransitioning}
										id="confirm-button"
									>
										{submitting ? (
											<>
												<Spinner animation="border" size="sm" className="me-2" />
												Updating...
											</>
										) : (
											"Update"
										)}
									</Button>
								</div>
								{/* Second row: Cancel */}
								<div className="modal-buttons-container">
									<Button
										variant="secondary"
										onClick={submode === "edit" ? handleHide : handleCancelEdit}
										disabled={isTransitioning}
										id="cancel-button"
									>
										{submode === "edit" ? "Close" : "Cancel"}
									</Button>
								</div>
							</div>
						</Modal.Footer>
					);
				}
			} else {
				return (
					<Modal.Footer>
						<div className="modal-buttons-container">
							<Button
								variant="secondary"
								onClick={handleHide}
								disabled={isTransitioning}
								id="cancel-button"
							>
								Close
							</Button>
							{fields.form && fields.form.length > 0 && (
								<Button
									variant="primary"
									onClick={handleEdit}
									disabled={isTransitioning}
									id="edit-button"
								>
									Edit
								</Button>
							)}
						</div>
					</Modal.Footer>
				);
			}
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
							id="cancel-button"
						>
							{cancelText}
						</Button>
					)}
					<Button onClick={handleSubmit} size="lg" style={{ minWidth: "100px" }} id="confirm-button">
						{confirmText}
					</Button>
				</Modal.Footer>
			);
		} else if (mode === "confirmation") {
			return (
				<Modal.Footer className={"modal-buttons-container"}>
					<Button variant="secondary" onClick={handleHide} id="cancel-button">
						{cancelText}
					</Button>
					<Button variant={confirmVariant} onClick={handleSubmit} id="confirm-button">
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
			{
				<Modal.Body ref={modalBodyRef} className={`${isTransitioning ? "modal-transitioning" : ""}`}>
					{renderBody()}
				</Modal.Body>
			}
			{renderFooter()}
		</>
	);

	const getModalId = () => {
		if (mode === "formview") {
			if (isEditing) {
				return `modal-${mode}-edit-${title.toLowerCase()}`;
			} else {
				return `modal-${mode}-view-${title.toLowerCase()}`;
			}
		}
		return `modal-${mode}`;
	};

	return (
		<Modal
			show={show}
			onHide={handleHide}
			size={size}
			centered={centered}
			backdrop={true}
			keyboard={true}
			id={getModalId()}
		>
			{mode === "formview" && isEditing ? <Form onSubmit={handleSubmit}>{modalContent}</Form> : modalContent}
		</Modal>
	);
};

export default GenericModal;
