import React, { useEffect, useRef, useState } from "react";
import { Alert, Button, Form, Modal, Spinner, Tab, Tabs } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import "./GenericModal.css";
import { renderFieldValue } from "../rendering/Renders";
import { renderInputField } from "../rendering/WidgetRenders";
import { api } from "../../services/Api";
import { viewFields as viewFieldsLib } from "../rendering/ViewRenders";
import useGenericAlert from "../../hooks/useGenericAlert";
import AlertModal from "./AlertModal";

/**
 * Creates a reusable delete handler for table items
 */
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
	// Basic modal props
	show, // Boolean - Controls modal visibility
	onHide, // Function - Called when modal should be closed
	itemName = "Entry", // String - Modal title text
	size = "lg", // String - Modal size: "sm", "md", "lg", "xl"
	centered = true, // Boolean - Whether to center modal vertically

	// Tab props
	tabs = null, // Array of tab objects: [{ key: "tab1", title: "Tab 1", mode, submode, fields, data, etc. }]
	defaultActiveTab = null, // String - Default active tab key
	onTabChange = null, // Function - Called when tab changes

	// Modal mode
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

	onDelete = null, // Function - Called after successful deletion
}) => {
	const { token } = useAuth();
	const [formData, setFormData] = useState(data || {});
	const [submitting, setSubmitting] = useState(false);
	const [errors, setErrors] = useState({});
	const [isEditing, setIsEditing] = useState(false); // State for formview mode
	const [isTransitioning, setIsTransitioning] = useState(false); // Animation state
	const [contentHeight, setContentHeight] = useState("auto"); // Height for smooth transitions
	const { alertState, showDelete, showError, hideAlert } = useGenericAlert();

	const [activeTab, setActiveTab] = useState(() => {
		if (tabs && tabs.length > 0) {
			return defaultActiveTab || tabs[0].key;
		}
		return null;
	});

	const previousShow = useRef(show);
	const modalBodyRef = useRef(null);
	const viewContentRef = useRef(null);
	const formContentRef = useRef(null);

	// Helper function to get current tab configuration
	const getCurrentTab = () => {
		if (!tabs || tabs.length === 0) return null;
		return tabs.find((tab) => tab.key === activeTab) || tabs[0];
	};

	// Helper function to get effective props (either from current tab or main props)
	const getEffectiveProps = () => {
		const currentTab = getCurrentTab();
		if (currentTab) {
			// Use tab-specific props, falling back to main props
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

		// No tabs - return original props (backward compatibility)
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

	// Reset form data and editing state when modal opens
	useEffect(() => {
		if (show && !previousShow.current) {
			const effectiveProps = getEffectiveProps();

			// Handle different submodes
			if (effectiveProps.submode === "add") {
				// Add submode
				setFormData({ ...effectiveProps.data });
				setIsEditing(true);
			} else if (effectiveProps.submode === "edit") {
				// Edit submode
				setFormData({ ...effectiveProps.data });
				setIsEditing(true);
			} else {
				// Default view submode
				setFormData({ ...effectiveProps.data });
				setIsEditing(false);
			}
			setErrors({});
			setIsTransitioning(false);
			setContentHeight("auto");

			// Reset active tab when modal opens (only if tabs are provided)
			if (tabs && tabs.length > 0) {
				setActiveTab(defaultActiveTab || tabs[0].key);
			}
		}
		previousShow.current = show;
	}, [show, data, submode, tabs, defaultActiveTab]);

	const getModalId = () => {
		if (isEditing) {
			return `modal-edit-${itemName.toLowerCase()}`;
		} else {
			return `modal-view-${itemName.toLowerCase()}`;
		}
	};

	// Notify parent component when form data changes
	useEffect(() => {
		const effectiveProps = getEffectiveProps();
		if (effectiveProps.onFormDataChange && isEditing) {
			effectiveProps.onFormDataChange(formData);
		}
	}, [formData, isEditing, activeTab]);

	// Handle tab change (only used when tabs are provided)
	const handleTabChange = (tabKey) => {
		if (!tabs) return;

		setActiveTab(tabKey);

		// Reset form state for new tab
		const newTab = tabs.find((tab) => tab.key === tabKey);
		if (newTab) {
			const newData = newTab.data || data;

			if (newTab.submode === "add") {
				setFormData({ ...newData });
				setIsEditing(true);
			} else if (newTab.submode === "edit") {
				setFormData({ ...newData });
				setIsEditing(true);
			} else {
				setFormData({ ...newData });
				setIsEditing(false);
			}

			setErrors({});
			setIsTransitioning(false);
			setContentHeight("auto");
		}

		if (onTabChange) {
			onTabChange(tabKey);
		}
	};

	// Handle modal hide
	const handleHide = () => {
		const effectiveProps = getEffectiveProps();

		if (effectiveProps.submode === "add") {
			setFormData({});
		} else {
			setFormData({ ...effectiveProps.data });
		}
		setErrors({});
		setSubmitting(false);
		setIsEditing(effectiveProps.submode === "add" || effectiveProps.submode === "edit");
		setIsTransitioning(false);
		setContentHeight("auto");

		// Reset active tab (only if tabs are provided)
		if (tabs && tabs.length > 0) {
			setActiveTab(defaultActiveTab || tabs[0].key);
		}

		onHide();
	};

	const measureContentHeight = (targetMode) => {
		// For tabbed modals, measure the actual visible tab content
		if (tabs && tabs.length > 0) {
			const activeTabPane = modalBodyRef.current?.querySelector(".tab-pane.active");
			if (activeTabPane) {
				// Create a temporary clone to measure the target mode content
				const clone = activeTabPane.cloneNode(true);
				clone.style.position = "absolute";
				clone.style.top = "-9999px";
				clone.style.left = "0";
				clone.style.right = "0";
				clone.style.visibility = "hidden";
				clone.style.height = "auto";

				// Show/hide the appropriate content in the clone based on target mode
				const visibleContent = clone.querySelector(".modal-content-visible");
				const hiddenFormContent = clone.querySelector(".modal-content-hidden:last-child");
				const hiddenViewContent = clone.querySelector(".modal-content-hidden:first-child");

				if (visibleContent && hiddenFormContent && hiddenViewContent) {
					if (targetMode === "form") {
						// Replace visible content with form content
						visibleContent.innerHTML = hiddenFormContent.innerHTML;
					} else {
						// Replace visible content with view content
						visibleContent.innerHTML = hiddenViewContent.innerHTML;
					}
				}

				// Add clone to DOM, measure, then remove
				modalBodyRef.current.appendChild(clone);
				const height = clone.scrollHeight;
				modalBodyRef.current.removeChild(clone);

				return height;
			}
		}

		const targetRef = targetMode === "form" ? formContentRef : viewContentRef;
		if (targetRef.current) {
			return targetRef.current.scrollHeight;
		}
		return "auto";
	};

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
			const effectiveProps = getEffectiveProps();
			setFormData({ ...effectiveProps.data });

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
			const effectiveProps = getEffectiveProps();
			setFormData({ ...effectiveProps.data });
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

	const handleDelete = createGenericDeleteHandler({
		endpoint: endpoint,
		token: token,
		showDelete: showDelete,
		showError: showError,
		removeItem: null,
		setData: null,
		itemType: itemName,
	});

	const handleDeleteClick = async () => {
		const effectiveProps = getEffectiveProps();
		const currentData = effectiveProps.data;

		try {
			await handleDelete(currentData);

			if (onDelete) {
				onDelete(currentData);
			}

			handleHide();
		} catch (error) {}
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
		const effectiveProps = getEffectiveProps();

		if (isEditing) {
			return effectiveProps.fields.form || effectiveProps.fields;
		} else {
			return effectiveProps.fields.view || effectiveProps.fields;
		}
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

	// Helper to get current data
	const getCurrentData = () => {
		const effectiveProps = getEffectiveProps();
		return effectiveProps.data;
	};

	const renderFormViewContent = () => {
		const effectiveProps = getEffectiveProps();
		const viewF = effectiveProps.fields.view || effectiveProps.fields;
		const formF = effectiveProps.fields.form || effectiveProps.fields;

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
							{effectiveProps.showSystemFields && (
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

				{/* Hidden content for measurement - ensure full width for tabs */}
				<div
					ref={viewContentRef}
					className="modal-content-hidden"
					style={{
						width: tabs && tabs.length > 0 ? "100%" : "auto",
					}}
				>
					<div>{viewF.map((item, index) => renderFieldGroup(item, index, false))}</div>
					{effectiveProps.showSystemFields && (
						<div className="mt-3 pt-3 border-top">
							{renderFieldGroup(
								[viewFieldsLib.createdAt(), viewFieldsLib.modifiedAt()],
								"system-fields",
								false,
							)}
						</div>
					)}
				</div>
				<div
					ref={formContentRef}
					className="modal-content-hidden"
					style={{
						width: tabs && tabs.length > 0 ? "100%" : "auto",
					}}
				>
					{errors.submit && <Alert variant="danger">{errors.submit}</Alert>}
					<div>{formF.map((item, index) => renderFieldGroup(item, index, true))}</div>
				</div>
			</>
		);
	};

	// NEW: Render custom tab content
	const renderCustomTabContent = (tab) => {
		if (tab.content) {
			return tab.content;
		}
		return null;
	};

	// Form validation
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
				// call the field's validator (sync or async)
				let result = field.validation(formData[field.name], formData);
				result = result instanceof Promise ? await result : result;

				// assume isValid=true if validator returned nothing
				const { isValid = true, message } = result || {};

				if (!isValid) {
					newErrors[field.name] = message;
				}
			}
		}

		// 3) Custom validation
		if (effectiveProps.validation && Object.keys(newErrors).length === 0) {
			if (typeof effectiveProps.validation === "function") {
				// Check if validation function is async
				const customErrorsResult = effectiveProps.validation(formData);

				// Handle both sync and async validation functions
				const customErrors =
					customErrorsResult instanceof Promise ? await customErrorsResult : customErrorsResult;

				// Append custom errors to existing errors
				Object.keys(customErrors).forEach((fieldName) => {
					if (newErrors[fieldName]) {
						// Append the custom error on a new line
						newErrors[fieldName] = `${newErrors[fieldName]}\n${customErrors[fieldName]}`;
					} else {
						// No existing error, just set the custom error
						newErrors[fieldName] = customErrors[fieldName];
					}
				});
			} else if (typeof effectiveProps.validation === "object") {
				// TODO remove?
				// Object-based validation (like current validationRules)
				const validationPromises = Object.keys(effectiveProps.validation).map(async (fieldName) => {
					const rule = effectiveProps.validation[fieldName];
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
						if (newErrors[result.fieldName]) {
							// Append the validation error on a new line
							newErrors[result.fieldName] = `${newErrors[result.fieldName]}\n${result.message}`;
						} else {
							// No existing error, just set the validation error
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

				// Call success callback
				if (effectiveProps.onSuccess) effectiveProps.onSuccess(result);

				// Handle post-submission behavior
				if (effectiveProps.submode === "add" || effectiveProps.submode === "edit") {
					handleHide();
				} else {
					// Update data and return to view mode
					Object.assign(getCurrentData(), result);
					await handleCancelEdit();
				}
			};

			// Use custom handler if provided, otherwise use default form data
			if (effectiveProps.customSubmitHandler) {
				await effectiveProps.customSubmitHandler(e.target, performSubmission);
			} else {
				await performSubmission(formData);
			}
		} catch (err) {
			console.error(
				`Error ${effectiveProps.submode === "add" ? "creating" : "updating"} ${itemName.toLowerCase()}:`,
				err,
			);

			// Use the error message from the API response if available
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

	// Modal header
	const renderHeader = () => {
		const effectiveProps = getEffectiveProps();

		// Icon & Title
		let icon;
		let text;
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

	// Render modal body content based on current tab or main content
	const renderBodyContent = () => {
		const currentTab = getCurrentTab();

		// Handle custom tab content
		if (currentTab && currentTab.content) {
			return renderCustomTabContent(currentTab);
		}

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
	};

	// Render modal body
	const renderBody = () => {
		// If we have tabs, render the tabs container
		if (tabs && tabs.length > 0) {
			return (
				<Tabs activeKey={activeTab} onSelect={handleTabChange} className="mb-3">
					{tabs.map((tab) => (
						<Tab key={tab.key} eventKey={tab.key} title={tab.title}>
							{renderBodyContent()}
						</Tab>
					))}
				</Tabs>
			);
		}

		return renderBodyContent();
	};

	// Render modal footer
	const renderFooter = () => {
		const effectiveProps = getEffectiveProps();

		if (isEditing) {
			if (effectiveProps.submode === "add") {
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
								<Button variant="danger" onClick={handleDeleteClick} className="me-auto">
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
									onClick={effectiveProps.submode === "edit" ? handleHide : handleCancelEdit}
									disabled={isTransitioning}
									id="cancel-button"
								>
									{effectiveProps.submode === "edit" ? "Close" : "Cancel"}
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
						<Button variant="secondary" onClick={handleHide} disabled={isTransitioning} id="cancel-button">
							Close
						</Button>
						{effectiveProps.fields.form && effectiveProps.fields.form.length > 0 && (
							<Button variant="primary" onClick={handleEdit} disabled={isTransitioning} id="edit-button">
								Edit
							</Button>
						)}
					</div>
				</Modal.Footer>
			);
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
				{(() => {
					return isEditing ? <Form onSubmit={handleSubmit}>{modalContent}</Form> : modalContent;
				})()}
			</Modal>
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};

export default GenericModal;
