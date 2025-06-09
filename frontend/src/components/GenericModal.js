import React, { useState, useEffect } from "react";
import { Modal, Form, Button, Alert } from "react-bootstrap";
import Select from "react-select";
import { useAuth } from "../contexts/AuthContext";
import "./GenericModal.css";

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
	fields = [], // Array - Field definitions for form mode
	initialData = {}, // Object - Initial form data
	endpoint, // String - API endpoint for form submission
	onSuccess, // Function - Called on successful form submission
	validationRules = {}, // Object - Custom validation rules for fields
	customValidation = null, // Function - Custom validation function
	transformFormData = null, // Function - Transform form data before submission
	isEdit = false, // Boolean - Whether form is in edit mode

	// Layout options
	useCustomLayout = false, // Boolean - Enable custom field layouts
	layoutGroups = [], // Array - Define groups of fields with custom layouts

	// View mode props
	data = null, // Object - Data to display in view mode
	viewFields = [], // Array - Field definitions for view mode display
	onEdit = null, // Function - Called when edit button is clicked
	showEditButton = true, // Boolean - Whether to show edit button in view mode
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
	customHeader = null, // React.Node - Custom header content
	customFooter = null, // React.Node - Custom footer content

	// Advanced customization
	headerClassName = "", // String - Additional CSS classes for header
	bodyClassName = "", // String - Additional CSS classes for body
	footerClassName = "", // String - Additional CSS classes for footer
	buttonContainerClassName = "modal-buttons-container", // String - CSS class for button container
}) => {
	const { token } = useAuth();
	const [formData, setFormData] = useState(initialData);
	const [submitting, setSubmitting] = useState(false);
	const [errors, setErrors] = useState({});

	// Reset form data when modal opens
	useEffect(() => {
		if (show && mode === "form") {
			setFormData({ ...initialData });
			setErrors({});
		}
	}, [show, initialData, mode]);

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
		setFormData((prev) => ({
			...prev,
			[name]: type === "checkbox" ? checked : value,
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

	// Custom styles for react-select
	const customSelectStyles = {
		control: (provided, state) => ({
			...provided,
			borderColor: errors[state.selectProps.name] ? "#dc3545" : "#dee2e6",
			boxShadow: state.isFocused ? "0 0 0 0.2rem rgba(13, 110, 253, 0.25)" : "none",
			"&:hover": {
				borderColor: errors[state.selectProps.name] ? "#dc3545" : "#86b7fe",
			},
			minHeight: "38px",
		}),
		valueContainer: (provided) => ({
			...provided,
			padding: "6px 12px",
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
		}),
		singleValue: (provided) => ({
			...provided,
			color: "#212529",
		}),
		menu: (provided) => ({
			...provided,
			zIndex: 9999,
		}),
		menuPortal: (provided) => ({
			...provided,
			zIndex: 9999,
		}),
	};

	// Form validation
	const validateForm = () => {
		const newErrors = {};

		// Get all fields from both regular fields and layout groups
		const allFields = useCustomLayout ? layoutGroups.flatMap((group) => group.fields || []).concat(fields) : fields;

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

	// Handle form submission
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
			const url = isEdit
				? `http://localhost:8000/${endpoint}/${initialData.id}/`
				: `http://localhost:8000/${endpoint}/`;

			const method = isEdit ? "PUT" : "POST";
			const dataToSubmit = transformFormData ? transformFormData(formData) : formData;

			const response = await fetch(url, {
				method: method,
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				body: JSON.stringify(dataToSubmit),
			});

			if (!response.ok) {
				throw new Error(`Failed to ${isEdit ? "update" : "create"} ${title.toLowerCase()}`);
			}

			const result = await response.json();
			onSuccess(result);
			handleHide();
		} catch (err) {
			console.error(`Error ${isEdit ? "updating" : "creating"} ${title.toLowerCase()}:`, err);
			setErrors({
				submit: `Failed to ${isEdit ? "update" : "create"} ${title.toLowerCase()}. Please try again.`,
			});
		} finally {
			setSubmitting(false);
		}
	};

	// Field rendering for forms
	const renderField = (field) => {
		// Handle custom render function
		if (field.render && typeof field.render === "function") {
			return field.render({
				value: formData[field.name] || "",
				onChange: handleChange,
				formData,
				errors,
				handleSelectChange,
			});
		}

		switch (field.type) {
			case "textarea":
				return (
					<Form.Control
						as="textarea"
						rows={field.rows || 3}
						name={field.name}
						value={formData[field.name] || ""}
						onChange={handleChange}
						placeholder={field.placeholder}
						isInvalid={!!errors[field.name]}
					/>
				);

			case "checkbox":
				return (
					<Form.Check
						type="checkbox"
						name={field.name}
						checked={formData[field.name] || false}
						onChange={handleChange}
						label={field.checkboxLabel || field.label}
					/>
				);

			case "select":
				return (
					<Form.Select
						name={field.name}
						value={formData[field.name] || ""}
						onChange={handleChange}
						isInvalid={!!errors[field.name]}
					>
						<option value="">Select {field.label}</option>
						{field.options?.map((option) => (
							<option key={option.value} value={option.value}>
								{option.label}
							</option>
						))}
					</Form.Select>
				);

			case "react-select":
				const selectedValue = field.options?.find((option) => option.value === formData[field.name]);

				return (
					<Select
						name={field.name}
						value={selectedValue || null}
						onChange={(selectedOption, actionMeta) => handleSelectChange(selectedOption, actionMeta)}
						options={field.options}
						placeholder={field.placeholder || `Select ${field.label}`}
						isSearchable={field.isSearchable}
						isClearable={field.isClearable}
						isDisabled={field.isDisabled}
						styles={customSelectStyles}
						menuPortalTarget={document.body}
						className="react-select-container"
						classNamePrefix="react-select"
					/>
				);

			default:
				return (
					<Form.Control
						type={field.type || "text"}
						name={field.name}
						value={formData[field.name] || ""}
						onChange={handleChange}
						placeholder={field.placeholder}
						isInvalid={!!errors[field.name]}
						step={field.step}
					/>
				);
		}
	};

	// Render a field group (for custom layouts)
	const renderFieldGroup = (group) => {
		if (group.type === "row") {
			return (
				<div key={group.id || Math.random()} className={`row ${group.className || ""}`}>
					{group.fields.map((field) => (
						<div key={field.name} className={field.columnClass || "col-md-6"}>
							<Form.Group className="mb-3">
								<Form.Label>
									{field.label}
									{field.required && <span className="text-danger">*</span>}
								</Form.Label>
								{renderField(field)}
								{errors[field.name] && (
									<div className="invalid-feedback d-block">{errors[field.name]}</div>
								)}
							</Form.Group>
						</div>
					))}
				</div>
			);
		}

		if (group.type === "custom") {
			return (
				<div key={group.id || Math.random()} className={group.className || ""}>
					{group.content}
				</div>
			);
		}

		// Default: full-width fields
		return (
			<div key={group.id || Math.random()}>
				{group.fields.map((field) => (
					<Form.Group key={field.name} className="mb-3">
						<Form.Label>
							{field.label}
							{field.required && <span className="text-danger">*</span>}
						</Form.Label>
						{renderField(field)}
						{errors[field.name] && <div className="invalid-feedback d-block">{errors[field.name]}</div>}
					</Form.Group>
				))}
			</div>
		);
	};

	// Field value rendering for view mode

	// Field value rendering for view mode
	const renderFieldValue = (field) => {
		// Check if field has a custom render function first
		if (field.render && typeof field.render === "function") {
			const rendered = field.render();
			// If render function returns null or undefined, show fallback
			if (rendered === null || rendered === undefined) {
				return <span className="text-muted">/</span>;
			}
			return rendered;
		}

		const value = data[field.name];

		switch (field.type) {
			case "checkbox":
				return <span className={`badge ${value ? "bg-success" : "bg-secondary"}`}>{value ? "Yes" : "No"}</span>;

			case "url":
				return value ? (
					<a href={value} target="_blank" rel="noopener noreferrer">
						{value}
					</a>
				) : (
					"No URL provided"
				);

			case "textarea":
				return value || `No ${field.label.toLowerCase()}`;

			case "select":
				if (field.options) {
					const option = field.options.find((opt) => opt.value === value);
					return option ? option.label : value || `No ${field.label.toLowerCase()}`;
				}
				return value || `No ${field.label.toLowerCase()}`;

			default:
				return value || `No ${field.label.toLowerCase()}`;
		}
	};

	// Helper functions for alert styling
	const getTypeVariant = (type) => {
		switch (type) {
			case "success":
				return "success";
			case "warning":
				return "warning";
			case "error":
				return "danger";
			default:
				return "primary";
		}
	};

	const getDefaultIcon = (type) => {
		switch (type) {
			case "success":
				return "bi-check-circle-fill";
			case "warning":
				return "bi-exclamation-triangle-fill";
			case "error":
				return "bi-x-circle-fill";
			default:
				return "bi-info-circle-fill";
		}
	};

	// Render modal header
	const renderHeader = () => {
		if (customHeader) return customHeader;

		const displayIcon = alertIcon || (mode === "alert" ? getDefaultIcon(alertType) : null);
		const headerClass = mode === "alert" ? `bg-${getTypeVariant(alertType)} bg-opacity-10` : "";

		return (
			<Modal.Header closeButton className={`${headerClass} ${headerClassName}`}>
				<Modal.Title className="d-flex align-items-center">
					{displayIcon && <i className={`${displayIcon} me-2`} style={{ fontSize: "1.2em" }} />}
					{mode === "view"
						? `${title} Details`
						: mode === "form"
							? `${isEdit ? "Edit" : "Add New"} ${title}`
							: title}
				</Modal.Title>
			</Modal.Header>
		);
	};

	// Render modal body
	const renderBody = () => {
		switch (mode) {
			case "form":
				return (
					<Modal.Body className={bodyClassName}>
						{errors.submit && <Alert variant="danger">{errors.submit}</Alert>}

						{customContent && <div className="mt-4">{customContent}</div>}

						{useCustomLayout ? (
							// Render custom layout groups
							<>
								{layoutGroups.map((group, index) => renderFieldGroup(group))}
								{/* Render any remaining fields not in groups */}
								{fields.length > 0 &&
									fields.map((field) => (
										<Form.Group key={field.name} className="mb-3">
											<Form.Label>
												{field.label}
												{field.required && <span className="text-danger">*</span>}
											</Form.Label>
											{renderField(field)}
											{errors[field.name] && (
												<div className="invalid-feedback d-block">{errors[field.name]}</div>
											)}
										</Form.Group>
									))}
							</>
						) : (
							// Render traditional layout
							<>
								{fields.map((field) => (
									<Form.Group key={field.name} className="mb-3">
										<Form.Label>
											{field.label}
											{field.required && <span className="text-danger">*</span>}
										</Form.Label>
										{renderField(field)}
										{errors[field.name] && (
											<div className="invalid-feedback d-block">{errors[field.name]}</div>
										)}
									</Form.Group>
								))}
							</>
						)}
					</Modal.Body>
				);

			case "view":
				if (!data) return null;

				return (
					<Modal.Body className={bodyClassName}>
						<div className="row">
							{viewFields.map((field) => (
								<div key={field.name} className={field.type === "textarea" ? "col-12" : "col-md-6"}>
									<h6>{field.label}</h6>
									<p>{renderFieldValue(field)}</p>
								</div>
							))}
						</div>
						<div className="mt-4">{customContent}</div>
						{showSystemFields && data.created_at && (
							<div className="row mt-3 pt-3 border-top">
								<div className="col-md-6">
									<h6>Date Added</h6>
									<p>{new Date(data.created_at).toLocaleDateString()}</p>
								</div>

								<div className="col-md-6">
									<h6>Last Updated</h6>
									<p>{new Date(data.modified_at).toLocaleDateString()}</p>
								</div>
							</div>
						)}
					</Modal.Body>
				);

			case "alert":
				return (
					<Modal.Body className={bodyClassName}>
						<div className="text-center py-3">
							{typeof alertMessage === "string" ? <p className="mb-0">{alertMessage}</p> : alertMessage}
						</div>
						<div className="mt-4">{customContent}</div>
					</Modal.Body>
				);

			case "confirmation":
				return (
					<Modal.Body className={bodyClassName}>
						<p className="mb-0">{confirmationMessage}</p>
						<div className="mt-4">{customContent}</div>
					</Modal.Body>
				);

			default:
				return <Modal.Body className={bodyClassName}>{customContent}</Modal.Body>;
		}
	};

	// Render modal footer
	const renderFooter = () => {
		if (customFooter) return customFooter;

		switch (mode) {
			case "form":
				return (
					<Modal.Footer className={footerClassName}>
						<div className={buttonContainerClassName}>
							<Button variant="secondary" onClick={handleHide}>
								Cancel
							</Button>
							<Button variant="primary" type="submit" disabled={submitting}>
								{submitting
									? isEdit
										? "Updating..."
										: "Saving..."
									: (isEdit ? "Update" : "Save") + ` ${title}`}
							</Button>
						</div>
					</Modal.Footer>
				);

			case "view":
				return (
					<Modal.Footer className={footerClassName}>
						<div className={buttonContainerClassName}>
							<Button variant="secondary" onClick={handleHide}>
								Close
							</Button>
							{showEditButton && onEdit && (
								<Button
									variant="primary"
									onClick={() => {
										onEdit(data);
									}}
								>
									Edit {title}
								</Button>
							)}
						</div>
					</Modal.Footer>
				);

			case "alert":
				return (
					<Modal.Footer className={`justify-content-center ${footerClassName}`}>
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
						<Button
							variant={getTypeVariant(alertType)}
							onClick={handleSubmit}
							size="lg"
							style={{ minWidth: "100px" }}
						>
							{confirmText}
						</Button>
					</Modal.Footer>
				);

			case "confirmation":
				return (
					<Modal.Footer className={footerClassName}>
						<Button variant="secondary" onClick={handleHide}>
							{cancelText}
						</Button>
						<Button variant={confirmVariant} onClick={handleSubmit}>
							{confirmText}
						</Button>
					</Modal.Footer>
				);

			default:
				return null;
		}
	};

	const modalContent = (
		<>
			{renderHeader()}
			{renderBody()}
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
