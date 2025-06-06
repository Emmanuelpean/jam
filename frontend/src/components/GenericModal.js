import React, { useEffect, useState } from "react";
import { Alert, Button, Form, Modal } from "react-bootstrap";
import Select from "react-select";
import { useAuth } from "../contexts/AuthContext";
import "./GenericModal.css";

const GenericModal = ({
	// Basic modal props
	show,
	onHide,
	title,
	size = "lg",
	centered = true,
	backdrop = null,
	keyboard = null,

	// Modal type and mode
	mode = "form", // 'form', 'view', 'alert', 'confirmation', 'custom'

	// Form mode props
	fields = [],
	initialData = {},
	endpoint,
	onSuccess,
	validationRules = {},
	customValidation = null,
	transformFormData = null,
	isEdit = false,

	// View mode props
	data = null,
	viewFields = [],
	onEdit = null,
	showEditButton = true,
	showSystemFields = true,

	// Alert mode props
	alertType = "info", // 'info', 'success', 'warning', 'error'
	alertMessage,
	alertIcon = null,
	confirmText = "OK",
	cancelText = "Cancel",
	showCancel = false,

	// Confirmation mode props
	confirmationMessage = "Are you sure you want to proceed?",
	onConfirm = null,
	confirmVariant = "danger",

	// Custom mode props
	customContent = null,
	customHeader = null,
	customFooter = null,

	// Advanced customization
	headerClassName = "",
	bodyClassName = "",
	footerClassName = "",
	buttonContainerClassName = "modal-buttons-container",
}) => {
	const { token } = useAuth();
	const [formData, setFormData] = useState(initialData);
	const [submitting, setSubmitting] = useState(false);
	const [errors, setErrors] = useState({});

	// Determine modal behavior based on mode
	const getModalBehavior = () => {
		if (backdrop !== null || keyboard !== null) {
			return {
				backdrop: backdrop !== null ? backdrop : true,
				keyboard: keyboard !== null ? keyboard : true,
			};
		}

		switch (mode) {
			case "alert":
			case "confirmation":
				return { backdrop: true, keyboard: true };
			case "form":
				return { backdrop: true, keyboard: true };
			default:
				return { backdrop: true, keyboard: true };
		}
	};

	const { backdrop: modalBackdrop, keyboard: modalKeyboard } = getModalBehavior();

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

		fields.forEach((field) => {
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
						isSearchable={field.isSearchable !== false}
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

	// Field value rendering for view mode
	const renderFieldValue = (field) => {
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
						<div className="mt-4">{customContent}</div>
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
									<p>{new Date(data.updated_at || data.created_at).toLocaleDateString()}</p>
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
										handleHide();
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
		<Modal
			show={show}
			onHide={handleHide}
			size={size}
			centered={centered}
			backdrop={modalBackdrop}
			keyboard={modalKeyboard}
		>
			{mode === "form" ? <Form onSubmit={handleSubmit}>{modalContent}</Form> : modalContent}
		</Modal>
	);
};

export default GenericModal;
