import React, { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Alert, Button, Card, Form, Modal, Spinner } from "react-bootstrap";
import { useAuth } from "../../../contexts/AuthContext";
import "./GenericModal.css";
import { renderFieldValue } from "../../rendering/view/Renders";
import { ActionButton, renderInputField } from "../../rendering/form/WidgetRenders";
import { api } from "../../../services/Api";
import useGenericAlert from "../../../hooks/useGenericAlert";
import AlertModal from "../AlertModal";

export const createGenericDeleteHandler = ({
	endpoint,
	token,
	showDelete,
	showError,
	removeItem,
	setData,
	itemType = "item",
}) => {
	return async (item) => {
		try {
			await showDelete({
				title: `Delete ${itemType}`,
				message: `Are you sure you want to delete this entry? This action cannot be undone.`,
				confirmText: "Delete",
				cancelText: "Cancel",
			});

			await api.delete(`${endpoint}/${item.id}`, token);

			if (typeof removeItem === "function") {
				removeItem(item.id);
			} else if (typeof setData === "function") {
				setData((prevData) => prevData.filter((dataItem) => dataItem.id !== item.id));
			} else {
				window.location.reload();
			}
		} catch (error) {
			if (error !== false) {
				await showError({
					message: `Failed to delete ${itemType}. Please check your connection and try again.`,
				});
			}
			throw error;
		}
	};
};

const GenericModal = ({
	show,
	onHide,
	itemName = "Entry",
	size = "lg",
	centered = true,
	tabs = null,
	defaultActiveTab = null,
	onTabChange = null,
	submode = "view",
	fields = {},
	data = null,
	endpoint,
	onSuccess,
	validation = null,
	transformFormData = null,
	customSubmitHandler = null,
	onFormDataChange = null,
	showSystemFields = true,
	onDelete = null,
}) => {
	const { token } = useAuth();
	const [formData, setFormData] = useState(data || {});
	const [originalFormData, setOriginalFormData] = useState(data || {}); // Track original data
	const [submitting, setSubmitting] = useState(false);
	const [errors, setErrors] = useState({});
	const [isEditing, setIsEditing] = useState(false);
	const [activeTab, setActiveTab] = useState(() => {
		if (tabs && tabs.length > 0) {
			return defaultActiveTab || tabs[0].key;
		}
		return null;
	});

	const [containerHeight, setContainerHeight] = useState("auto");
	const contentRef = useRef(null);
	const previousShow = useRef(show);
	const { alertState, showDelete, showError, hideAlert } = useGenericAlert();

	// Helper to check if form data has been modified
	const hasUnsavedChanges = () => {
		if (!isEditing) return false;

		// Compare current form data with original
		const currentKeys = Object.keys(formData);
		const originalKeys = Object.keys(originalFormData);

		// Check if different number of keys
		if (currentKeys.length !== originalKeys.length) return true;

		// Check if any values are different
		return currentKeys.some((key) => {
			const currentValue = formData[key];
			const originalValue = originalFormData[key];

			// Handle null/undefined/empty string equivalence
			if (
				(currentValue === null || currentValue === undefined || currentValue === "") &&
				(originalValue === null || originalValue === undefined || originalValue === "")
			) {
				return false;
			}

			// Handle arrays (for multi-select fields)
			if (Array.isArray(currentValue) && Array.isArray(originalValue)) {
				if (currentValue.length !== originalValue.length) return true;
				return currentValue.some((val, index) => val !== originalValue[index]);
			}

			return currentValue !== originalValue;
		});
	};

	// Confirmation handler for closing with unsaved changes
	const handleCloseWithConfirmation = async (showConfirmation = true) => {
		if (showConfirmation && hasUnsavedChanges()) {
			try {
				await showDelete({
					title: "Unsaved Changes",
					message: "You have unsaved changes. Are you sure you want to close without saving?",
					confirmText: "Close without saving",
					cancelText: "Cancel",
				});
				// If confirmed, proceed with normal close
				handleHideImmediate();
			} catch (error) {
				// User cancelled, do nothing
			}
		} else {
			// No unsaved changes or confirmation disabled, close normally
			handleHideImmediate();
		}
	};

	// Immediate hide without confirmation (used internally)
	const handleHideImmediate = () => {
		const effectiveProps = getEffectiveProps();

		if (effectiveProps.submode === "add") {
			setFormData({});
			setOriginalFormData({});
		} else {
			setFormData({ ...effectiveProps.data });
			setOriginalFormData({ ...effectiveProps.data });
		}
		setErrors({});
		setSubmitting(false);
		setIsEditing(effectiveProps.submode === "add" || effectiveProps.submode === "edit");
		if (tabs && tabs.length > 0) {
			setActiveTab(defaultActiveTab || tabs[0].key);
		}
		onHide();
	};

	// Helper to get current tab config
	const getCurrentTab = () => {
		if (!tabs || tabs.length === 0) return null;
		return tabs.find((tab) => tab.key === activeTab) || tabs[0];
	};

	// Helper to get effective props either from tab or main props
	const getEffectiveProps = () => {
		const currentTab = getCurrentTab();
		if (currentTab) {
			return {
				submode: currentTab.submode !== undefined ? currentTab.submode : submode,
				fields: currentTab.fields !== undefined ? currentTab.fields : fields,
				data: currentTab.data !== undefined ? currentTab.data : data,
				endpoint: currentTab.endpoint !== undefined ? currentTab.endpoint : endpoint,
				onSuccess: currentTab.onSuccess !== undefined ? currentTab.onSuccess : onSuccess,
				validation: currentTab.validation !== undefined ? currentTab.validation : validation,
				transformFormData:
					currentTab.transformFormData !== undefined ? currentTab.transformFormData : transformFormData,
				customSubmitHandler:
					currentTab.customSubmitHandler !== undefined ? currentTab.customSubmitHandler : customSubmitHandler,
				onFormDataChange:
					currentTab.onFormDataChange !== undefined ? currentTab.onFormDataChange : onFormDataChange,
				showSystemFields:
					currentTab.showSystemFields !== undefined ? currentTab.showSystemFields : showSystemFields,
				onDelete: currentTab.onDelete !== undefined ? currentTab.onDelete : onDelete,
			};
		}
		return {
			submode,
			fields,
			data,
			endpoint,
			onSuccess,
			validation,
			transformFormData,
			customSubmitHandler,
			onFormDataChange,
			showSystemFields,
		};
	};

	useEffect(() => {
		if (show && !previousShow.current) {
			const effectiveProps = getEffectiveProps();

			if (effectiveProps.submode === "add") {
				setFormData({ ...effectiveProps.data });
				setOriginalFormData({ ...effectiveProps.data });
				setIsEditing(true);
			} else if (effectiveProps.submode === "edit") {
				setFormData({ ...effectiveProps.data });
				setOriginalFormData({ ...effectiveProps.data });
				setIsEditing(true);
			} else {
				setFormData({ ...effectiveProps.data });
				setOriginalFormData({ ...effectiveProps.data });
				setIsEditing(false);
			}
			setErrors({});
			if (tabs && tabs.length > 0) {
				setActiveTab(defaultActiveTab || tabs[0].key);
			}
		}
		previousShow.current = show;
	}, [show, data, submode, tabs, defaultActiveTab]);

	useEffect(() => {
		const effectiveProps = getEffectiveProps();
		if (effectiveProps.onFormDataChange && isEditing) {
			effectiveProps.onFormDataChange(formData);
		}
	}, [formData, isEditing, activeTab]);

	const handleTabChange = (tabKey) => {
		if (!tabs) return;
		setActiveTab(tabKey);
		const newTab = tabs.find((tab) => tab.key === tabKey);
		if (newTab) {
			const newData = newTab.data || data;

			if (newTab.submode === "add") {
				setFormData({ ...newData });
				setOriginalFormData({ ...newData });
				setIsEditing(true);
			} else if (newTab.submode === "edit") {
				setFormData({ ...newData });
				setOriginalFormData({ ...newData });
				setIsEditing(true);
			} else {
				setFormData({ ...newData });
				setOriginalFormData({ ...newData });
				setIsEditing(false);
			}
			setErrors({});
		}
		if (onTabChange) {
			onTabChange(tabKey);
		}
	};

	// Main hide handler - shows confirmation for ESC/backdrop, not for button clicks
	const handleHide = () => handleCloseWithConfirmation(true);

	// Cancel edit handler - no confirmation, always direct action
	const handleCancelEdit = () => {
		setIsEditing(false);
		const effectiveProps = getEffectiveProps();
		setFormData({ ...effectiveProps.data });
		setOriginalFormData({ ...effectiveProps.data });
		setErrors({});
	};

	// Cancel/Close button handler - no confirmation, always direct action
	const handleCancelClose = () => handleCloseWithConfirmation(false);

	// useLayoutEffect(() => {
	// 	if (contentRef.current?.scrollHeight) {
	// 		setContainerHeight(contentRef.current);
	// 		requestAnimationFrame(() => {
	// 			setContainerHeight(contentRef.current.scrollHeight + "px");
	// 		});
	// 	}
	// }, [isEditing, activeTab, fields, data]);

	useLayoutEffect(() => {
		if (!contentRef.current) return;

		const updateHeight = () => {
			if (contentRef.current?.scrollHeight) {
				setContainerHeight(String(Number(contentRef.current.scrollHeight) + 1) + "px");
			}
		};

		// Initial height calculation
		updateHeight();

		// Create ResizeObserver to watch for content size changes
		const resizeObserver = new ResizeObserver(() => {
			// Remove requestAnimationFrame for immediate updates
			updateHeight();
		});

		// Observe the content element
		resizeObserver.observe(contentRef.current);

		// Also observe all child elements that might change size
		const childElements = contentRef.current.querySelectorAll("*");
		childElements.forEach((el) => {
			resizeObserver.observe(el);
		});

		// Cleanup
		return () => {
			resizeObserver.disconnect();
		};
	}, [isEditing, activeTab, fields, data]);

	// Helpers for fields, rendering, data
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

	const getCurrentFields = () => {
		const effectiveProps = getEffectiveProps();
		if (isEditing) {
			return effectiveProps.fields.form || effectiveProps.fields;
		} else {
			return effectiveProps.fields.view || effectiveProps.fields;
		}
	};

	const getCurrentData = () => {
		const effectiveProps = getEffectiveProps();
		return effectiveProps.data;
	};

	const renderFieldGroup = (item, index, isFormMode = true) => {
		if (item.name || item.key) {
			item = [item];
		}

		const renderTitleField = (field) => (
			<div className="text-center p-1">
				<h2 className="display-6 fw-bold mt-4 mb-4" style={{ color: "var(--primary-mid)" }}>
					{renderFieldValue(field, getCurrentData(), getModalId())}
				</h2>
			</div>
		);

		if (!isEditing) {
			if (item[0].isTitle && item.length === 1) {
				const currentFields = getCurrentFields();
				const hasElementsUnderneath = index < currentFields.length - 1;

				return <div className={hasElementsUnderneath ? "mb-3" : ""}>{renderTitleField(item[0])}</div>;
			}
		}

		if (Array.isArray(item)) {
			const getColumnClass = (count) => {
				switch (count) {
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
					{item.map((field, fieldIndex) => (
						<div key={field.key || field.name || `field_${index}_${fieldIndex}`} className={columnClass}>
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
									<div className="mb-3">
										{renderFieldValue(field, getCurrentData(), getModalId())}
									</div>
								</div>
							)}
						</div>
					))}
				</div>
			);
		}
		return null;
	};

	const renderContent = () => {
		const effectiveProps = getEffectiveProps();
		const viewF = effectiveProps.fields.view || effectiveProps.fields;
		const formF = effectiveProps.fields.form || effectiveProps.fields;

		return (
			<>
				<div className={`modal-content-visible`}>
					{isEditing ? (
						<div>
							{errors.submit && <Alert variant="danger">{errors.submit}</Alert>}
							<div>
								{formF.map((item, index) => (
									<div key={`form-field-${index}`}>{renderFieldGroup(item, index, true)}</div>
								))}
							</div>
						</div>
					) : (
						<div>
							<Card>
								<Card.Body>
									<div>
										{viewF.map((item, index) => (
											<div key={`view-field-${index}`}>
												{renderFieldGroup(item, index, false)}
											</div>
										))}
									</div>
								</Card.Body>
							</Card>
						</div>
					)}
				</div>
			</>
		);
	};

	const handleEdit = () => {
		setIsEditing(true);
		const effectiveProps = getEffectiveProps();
		setFormData({ ...effectiveProps.data });
		setOriginalFormData({ ...effectiveProps.data });
	};

	const handleDelete = createGenericDeleteHandler({
		endpoint,
		token,
		showDelete,
		showError,
		removeItem: null,
		setData: null,
		itemType: itemName,
	});

	const handleDeleteClick = async () => {
		const effectiveProps = getEffectiveProps();
		try {
			await handleDelete(effectiveProps.data);
			if (onDelete) {
				onDelete(effectiveProps.data);
			}
			handleHideImmediate();
		} catch (error) {}
	};

	const handleChange = (e) => {
		const { name, value, type, checked } = e.target;
		let newValue;
		if (type === "checkbox") {
			newValue = checked;
		} else if (type === "file") {
			newValue = value;
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

	const validateForm = async () => {
		const newErrors = {};
		const currentFields = getCurrentFields();
		const allFields = extractAllFields(currentFields);
		const effectiveProps = getEffectiveProps();

		// 1) Required field validation
		allFields.forEach((field) => {
			if (field.required && !formData[field.name]) {
				newErrors[field.name] = `${field.label} is required`;
			}
		});

		// 2) Per‐field custom validation
		for (const field of allFields) {
			if (field.validation) {
				let result = field.validation(formData[field.name], formData);
				result = result instanceof Promise ? await result : result;
				const { isValid = true, message } = result || {};
				if (!isValid) {
					newErrors[field.name] = message;
				}
			}
		}

		// 3) Custom validation
		if (effectiveProps.validation && Object.keys(newErrors).length === 0) {
			if (typeof effectiveProps.validation === "function") {
				const customErrorsResult = effectiveProps.validation(formData);
				const customErrors =
					customErrorsResult instanceof Promise ? await customErrorsResult : customErrorsResult;
				Object.keys(customErrors).forEach((fieldName) => {
					if (newErrors[fieldName]) {
						newErrors[fieldName] = `${newErrors[fieldName]}\n${customErrors[fieldName]}`;
					} else {
						newErrors[fieldName] = customErrors[fieldName];
					}
				});
			} else if (typeof effectiveProps.validation === "object") {
				// TODO remove?
				// Object-based validation (like current validationRules)
				const validationPromises = Object.keys(effectiveProps.validation).map(async (fieldName) => {
					const rule = effectiveProps.validation[fieldName];
					const result = rule(formData[fieldName], formData);
					const validationResult = result instanceof Promise ? await result : result;
					if (!validationResult.isValid) {
						return { fieldName, message: validationResult.message };
					}
					return null;
				});
				const validationResults = await Promise.all(validationPromises);
				validationResults.forEach((result) => {
					if (result) {
						if (newErrors[result.fieldName]) {
							newErrors[result.fieldName] = `${newErrors[result.fieldName]}\n${result.message}`;
						} else {
							newErrors[result.fieldName] = result.message;
						}
					}
				});
			}
		}

		return newErrors;
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		const effectiveProps = getEffectiveProps();
		setSubmitting(true);
		setErrors({});
		try {
			const validationErrors = await validateForm();
			if (Object.keys(validationErrors).length > 0) {
				setErrors(validationErrors);
				setSubmitting(false);
				return;
			}
			const performSubmission = async (processedData) => {
				const dataToSubmit = effectiveProps.transformFormData
					? effectiveProps.transformFormData(processedData)
					: processedData;
				let result;
				if (effectiveProps.submode === "add") {
					result = await api.post(`${effectiveProps.endpoint}/`, dataToSubmit, token);
				} else {
					const itemId = getCurrentData()?.id;
					result = await api.put(`${effectiveProps.endpoint}/${itemId}`, dataToSubmit, token);
				}
				if (effectiveProps.onSuccess) effectiveProps.onSuccess(result);
				if (effectiveProps.submode === "add" || effectiveProps.submode === "edit") {
					handleHideImmediate();
				} else {
					Object.assign(getCurrentData(), result);
					await handleCancelEdit();
				}
			};
			if (effectiveProps.customSubmitHandler) {
				await effectiveProps.customSubmitHandler(e.target, performSubmission);
			} else {
				await performSubmission(formData);
			}
		} catch (err) {
			const errorMessage =
				err.data?.detail ||
				err.message ||
				`Failed to ${effectiveProps.submode === "add" ? "create" : "update"} ${itemName.toLowerCase()}. Please try again.`;
			setErrors({
				submit: errorMessage,
			});
		} finally {
			setSubmitting(false);
		}
	};

	const getModalId = () => {
		if (isEditing) {
			return `modal-edit-${itemName.toLowerCase()}`;
		} else {
			return `modal-view-${itemName.toLowerCase()}`;
		}
	};

	const renderHeader = () => {
		const effectiveProps = getEffectiveProps();
		let icon, text;
		if (effectiveProps.submode === "add") {
			icon = "bi bi-plus-circle";
			text = `Add New ${itemName}`;
		} else if (effectiveProps.submode === "edit" || isEditing) {
			icon = "bi bi-pencil";
			text = `Edit ${itemName}`;
		} else {
			icon = "bi bi-eye";
			text = `${itemName} Details`;
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

	const renderBodyContent = () => {
		const currentTab = getCurrentTab();
		if (currentTab && currentTab.content) {
			return currentTab.content;
		}
		return (
			<div className="modal-content-animated" style={{ height: containerHeight }}>
				<div ref={contentRef}>{renderContent()}</div>
			</div>
		);
	};

	const renderBody = () => {
		// If we have tabs, render custom tab buttons instead of Bootstrap Tabs
		if (tabs && tabs.length > 0) {
			return (
				<>
					{/* Custom Tab Navigation */}
					<div className="custom-tab-nav">
						{tabs.map((tab) => (
							<button
								key={tab.key}
								type="button"
								className={`custom-tab-button ${activeTab === tab.key ? "active" : ""}`}
								onClick={() => handleTabChange(tab.key)}
							>
								{tab.title}
							</button>
						))}
					</div>

					{/* Tab Content */}
					<div className="custom-tab-content">{renderBodyContent()}</div>
				</>
			);
		}
		return renderBodyContent();
	};

	const renderFooter = () => {
		const effectiveProps = getEffectiveProps();
		if (isEditing) {
			if (effectiveProps.submode === "add") {
				return (
					<Modal.Footer>
						<div className="d-flex flex-column w-100 gap-2">
							<div className="modal-buttons-container">
								<ActionButton
									id="cancel-button"
									variant="secondary"
									onClick={handleCancelClose}
									defaultText="Cancel"
									fullWidth={false}
								/>
								<ActionButton
									id="confirm-button"
									type="submit"
									disabled={submitting}
									loading={submitting}
									loadingText="Submitting..."
									defaultText="Confirm"
									fullWidth={false}
								/>
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
								<ActionButton
									variant="danger"
									onClick={handleDeleteClick}
									className="me-auto"
									defaultText="Delete"
									defaultIcon="bi bi-trash"
									fullWidth={false}
								/>

								<ActionButton
									id="confirm-button"
									type="submit"
									disabled={submitting}
									loading={submitting}
									loadingText="Updating..."
									defaultText="Update"
									fullWidth={false}
								/>
							</div>
							{/* Second row: Cancel */}
							<div className="modal-buttons-container">
								<ActionButton
									id="cancel-button"
									variant="secondary"
									onClick={effectiveProps.submode === "edit" ? handleCancelClose : handleCancelEdit}
									defaultText={effectiveProps.submode === "edit" ? "Close" : "Cancel"}
									fullWidth={false}
								/>
							</div>
						</div>
					</Modal.Footer>
				);
			}
		} else {
			return (
				<Modal.Footer>
					<div className="modal-buttons-container">
						<ActionButton
							id="cancel-button"
							variant="secondary"
							onClick={handleCancelClose}
							defaultText="Close"
							fullWidth={false}
						/>
						{effectiveProps.fields.form && effectiveProps.fields.form.length > 0 && (
							<ActionButton
								id="edit-button"
								variant="primary"
								onClick={handleEdit}
								defaultText="Edit"
								fullWidth={false}
							/>
						)}
					</div>
				</Modal.Footer>
			);
		}
	};

	const modalContent = (
		<>
			{renderHeader()}
			<Modal.Body>{renderBody()}</Modal.Body>
			{renderFooter()}
		</>
	);

	return (
		<>
			<Modal
				show={show}
				onHide={handleHide}
				size={size}
				centered={centered}
				backdrop={true}
				keyboard={true}
				id={getModalId()}
			>
				{isEditing ? <Form onSubmit={handleSubmit}>{modalContent}</Form> : modalContent}
			</Modal>
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};

export default GenericModal;
