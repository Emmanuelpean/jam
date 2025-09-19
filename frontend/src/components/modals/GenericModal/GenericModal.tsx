import React, { JSX, ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";
import { Alert, Card, Form, Modal, Spinner } from "react-bootstrap";
import { useAuth } from "../../../contexts/AuthContext";
import "./GenericModal.css";
import { renderViewElement } from "../../rendering/view/ViewRenders";
import { Errors, renderFormField, SyntheticEvent } from "../../rendering/widgets/WidgetRenders";
import { ActionButton } from "../../rendering/form/ActionButton";
import { api } from "../../../services/Api";
import useGenericAlert from "../../../hooks/useGenericAlert";
import AlertModal from "../AlertModal";
import { areDifferent, findByKey, flattenArray } from "../../../utils/Utils";
import { renderViewField, ViewField } from "../../rendering/view/ModalFieldRenders";
import { FormField } from "../../rendering/form/FormRenders";

interface CreateGenericDeleteHandlerParams {
	endpoint: string;
	token: string | null;
	showDelete: (options: {
		title: string;
		message: string;
		confirmText: string;
		cancelText: string;
	}) => Promise<boolean>;
	showError: (options: { message: string }) => Promise<boolean>;
	removeItem?: (id: string | number) => void;
	setData?: React.Dispatch<React.SetStateAction<any[]>>;
	itemType?: string;
}

interface DeleteHandlerItem {
	id: string | number;
}

export const createGenericDeleteHandler = ({
	endpoint,
	token,
	showDelete,
	showError,
	removeItem,
	setData,
	itemType = "item",
}: CreateGenericDeleteHandlerParams) => {
	return async (item: DeleteHandlerItem): Promise<void> => {
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
				setData((prevData: any[]) => prevData.filter((dataItem: any) => dataItem.id !== item.id));
			} else {
				window.location.reload();
			}
		} catch (error) {
			if (error !== false) {
				await showError({
					message: `Failed to delete ${itemType}.`,
				});
			}
			throw error;
		}
	};
};

export type ViewFields = (ViewField | ViewField[])[];
export type FormFields = (FormField | FormField[])[];

interface ModalProps {
	mode?: "view" | "edit" | "add";
	fields: { view: ViewFields; form: FormFields };
	data?: any;
	id?: string | number | null;
	onSuccess?: (data: any) => void;
	validation?: ((data: any) => any) | null;
	transformFormData?: ((data: any) => any) | null;
	onFormDataChange?: ((data: any) => void) | null;
	onDelete?: ((item: any) => Promise<void>) | null;
	additionalFields?: ViewField[];
}

export interface TabConfig {
	key: string;
	title: string | JSX.Element | ((data: any) => ReactNode);
	fields: { view: ViewFields; form: FormFields };
	additionalFields?: ViewField[];
}

export interface GenericModalProps extends ModalProps {
	show: boolean;
	onHide: () => void;
	itemName?: string;
	size?: "sm" | "lg" | "xl";
	tabs?: TabConfig[] | null;
	defaultActiveTab?: string | null;
	endpoint: string;
}

export interface ValidationErrors {
	[key: string]: string;
}

const GenericModal = ({
	show,
	onHide,
	fields,
	itemName = "Entry",
	size = "lg",
	tabs = null,
	defaultActiveTab = null,
	mode = "view",
	additionalFields = [],
	data = null,
	id = null,
	endpoint,
	onSuccess,
	validation = null,
	transformFormData = null,
	onFormDataChange = null,
	onDelete = null,
}: GenericModalProps) => {
	const hasTabs = tabs && tabs.length > 0;

	const { token } = useAuth();
	const [effectiveData, setEffectiveData] = useState(data);
	const [formData, setFormData] = useState<Record<string, any>>({});
	const [originalFormData, setOriginalFormData] = useState<Record<string, any>>({});
	const [submitting, setSubmitting] = useState(false);
	const [errors, setErrors] = useState<Errors>({});
	const [isEditing, setIsEditing] = useState(false);
	const [loading, setLoading] = useState(false);
	const [activeTab, setActiveTab] = useState<string | null>(() => {
		if (hasTabs) {
			return defaultActiveTab || tabs[0]!.key;
		}
		return null;
	});
	const [containerHeight, setContainerHeight] = useState("auto");
	const contentRef = useRef<HTMLDivElement>(null);
	const previousShow = useRef(show);
	const { alertState, showDelete, showError, hideAlert } = useGenericAlert();

	// -------------------------------------------------- DATA LOADING -------------------------------------------------

	useEffect(() => {
		const loadData = async () => {
			if (show && endpoint && token) {
				if (id) {
					setLoading(true);
					try {
						const response = await api.get(`${endpoint}/${id}`, token);
						if (response) {
							setEffectiveData(response);
						}
					} catch (error) {
						console.error(`Failed to load ${itemName}:`, error);
						await showError({
							message: `Failed to load ${itemName}.`,
						});
					} finally {
						setLoading(false);
					}
				} else if (data) {
					setEffectiveData(data);
				}
			}
		};

		loadData().then(() => {});
	}, [id, endpoint, token, data]);

	// ------------------------------------------------ MODAL STATE INIT ------------------------------------------------

	const getCurrentTabConfig = (): TabConfig | null => {
		if (!hasTabs) return null;
		return findByKey(tabs, activeTab) || tabs[0];
	};

	const getCurrentFields = (): { view: ViewFields; form: FormFields } => {
		const currentTab = getCurrentTabConfig();
		if (!currentTab) {
			return fields;
		}
		const formFields = filterConditionalFields(currentTab.fields.form);
		const viewFields = filterConditionalFields(currentTab.fields.view);
		return { form: formFields, view: viewFields };
	};

	const getCurrentAdditionalFields = (): ViewField[] => {
		const currentTab = getCurrentTabConfig();
		return currentTab?.additionalFields || additionalFields;
	};

	useEffect(() => {
		// Initialize modal state when it becomes visible or data changes
		if (show && (!previousShow.current || (effectiveData && Object.keys(formData).length === 0))) {
			if (mode === "add") {
				setFormData({});
				setOriginalFormData({});
				setIsEditing(true);
			} else if (mode === "edit") {
				setFormData({ ...effectiveData });
				setOriginalFormData({ ...effectiveData });
				setIsEditing(true);
			} else {
				setFormData({ ...effectiveData });
				setOriginalFormData({ ...effectiveData });
				setIsEditing(false);
			}
			setErrors({});

			// Reset active tab only when modal first opens
			if (hasTabs && !previousShow.current) {
				setActiveTab(defaultActiveTab || tabs[0]!.key);
			}
		}
		previousShow.current = show;
	}, [show, effectiveData, mode, tabs, defaultActiveTab]);

	// Simple tab change - just update the active tab, keep shared editing state
	const handleTabChange = (tabKey: string): void => {
		setActiveTab(tabKey);
		setErrors({}); // Clear errors when switching tabs
	};

	useEffect(() => {
		// Allow dynamic form fields based on current data
		if (onFormDataChange && isEditing) {
			onFormDataChange(formData);
		}
	}, [formData, isEditing, onFormDataChange]);

	// ---------------------------------------------------- CLOSING ----------------------------------------------------

	const hasUnsavedChanges = (): boolean => {
		if (!isEditing) return false;
		const keys: string[] = Object.keys(formData);
		return keys.some((key: string) => {
			const currentValue: any = formData[key];
			const originalValue: any = originalFormData[key];
			return areDifferent(currentValue, originalValue);
		});
	};

	const handleCloseWithConfirmation = async () => {
		if (hasUnsavedChanges()) {
			try {
				await showDelete({
					title: "Unsaved Changes",
					message: "You have unsaved changes. Are you sure you want to close without saving?",
					confirmText: "Close without saving",
					cancelText: "Cancel",
				});
				handleHideImmediate();
			} catch (error) {
				// User cancelled, do nothing
			}
		} else {
			handleHideImmediate();
		}
	};

	const handleHideImmediate = (): void => {
		onHide();
	};

	// ---------------------------------------------------- EDITING ----------------------------------------------------

	const handleEditToView = (): void => {
		setIsEditing(false);
		setFormData({ ...effectiveData });
		setOriginalFormData({ ...effectiveData });
		setErrors({});
	};

	const handleEdit = () => {
		setIsEditing(true);
		setFormData({ ...effectiveData });
		setOriginalFormData({ ...effectiveData });
	};

	// ----------------------------------------------------- LAYOUT ----------------------------------------------------

	useLayoutEffect(() => {
		if (!contentRef.current) return;

		const updateHeight = (): void => {
			if (contentRef.current?.scrollHeight) {
				setContainerHeight(String(Number(contentRef.current.scrollHeight) + 1) + "px");
			}
		};

		updateHeight();

		const resizeObserver = new ResizeObserver(() => {
			updateHeight();
		});

		resizeObserver.observe(contentRef.current);

		const childElements = contentRef.current.querySelectorAll("*");
		childElements.forEach((el: Element) => {
			resizeObserver.observe(el);
		});

		return () => {
			resizeObserver.disconnect();
		};
	}, [isEditing, activeTab, effectiveData]);

	// ------------------------------------------------- MODAL CONTENT -------------------------------------------------

	const renderFieldGroup = (
		item: ViewField | FormField | ViewField[] | FormField[],
		index: number,
		isFormMode = true,
	) => {
		let itemList: ViewField[] | FormField[];
		if (Array.isArray(item)) {
			itemList = item;
		} else {
			itemList = [item] as ViewField[] | FormField[];
		}

		if (!isEditing && itemList.length === 1) {
			const firstItem = itemList[0];
			if (firstItem && "isTitle" in firstItem && firstItem.isTitle) {
				const currentFields = getCurrentFields();
				const fieldsToCheck = isFormMode ? currentFields.form : currentFields.view;
				const hasElementsUnderneath = index < fieldsToCheck.length - 1;

				return (
					<div className={hasElementsUnderneath ? "mb-3" : ""} key={index}>
						{renderViewField(firstItem as ViewField, effectiveData, getModalId())}
					</div>
				);
			}
		}

		const getColumnClass = (count: number): string => {
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
		const columnClass = getColumnClass(itemList.length);

		return (
			<div key={index} className="row mb-3" style={{ paddingRight: "0.3rem", paddingLeft: "0.3rem" }}>
				{itemList.map((field: ViewField | FormField, fieldIndex: number) => {
					const fieldKey =
						("key" in field ? field.key : null) ||
						("name" in field ? field.name : null) ||
						`field_${index}_${fieldIndex}`;

					return (
						<div key={fieldKey} className={columnClass}>
							{isFormMode
								? renderFormField(field as FormField, formData, handleChange, errors)
								: renderViewField(field as ViewField, effectiveData, getModalId())}
						</div>
					);
				})}
			</div>
		);
	};

	// ----------------------------------------------------- DELETE ----------------------------------------------------

	const handleDelete = createGenericDeleteHandler({
		endpoint,
		token,
		showDelete,
		showError,
		removeItem: undefined,
		setData: undefined,
		itemType: itemName,
	});

	const handleDeleteClick = async () => {
		try {
			await handleDelete(effectiveData);
			if (onDelete) {
				await onDelete(effectiveData);
			}
			handleHideImmediate();
		} catch (error) {
			// Error already handled by createGenericDeleteHandler
		}
	};

	const handleChange = (e: SyntheticEvent) => {
		const { name, value } = e.target;
		setFormData((prev) => ({
			...prev,
			[name]: value,
		}));
		if (errors[name]) {
			setErrors((prev) => ({ ...prev, [name]: "" }));
		}
	};

	const filterConditionalFields = <T extends ViewField | FormField>(fieldsToFilter: (T | T[])[]): (T | T[])[] => {
		return fieldsToFilter
			.map((item) => {
				if (Array.isArray(item)) {
					const filteredArray = item.filter((field) => {
						if (!field.condition) {
							return true;
						} else {
							return field.condition(formData);
						}
					});
					return filteredArray.length > 0 ? filteredArray : null;
				} else {
					if (!item.condition) {
						return item;
					} else {
						return item.condition(formData) ? item : null;
					}
				}
			})
			.filter((item) => item !== null) as (T | T[])[];
	};

	const validateFormFields = async (): Promise<Errors> => {
		const newErrors: Errors = {};
		const currentFields = getCurrentFields();
		const allFields = flattenArray(currentFields.form);

		// 1) Required field validation
		allFields.forEach((field): void => {
			if (field.required && !formData[field.name]) {
				newErrors[field.name] = `${field.label} is required`;
			}
		});

		// 2) Field custom validation
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

		// 3) Custom entry validation
		if (validation && Object.keys(newErrors).length === 0) {
			if (typeof validation === "function") {
				const customErrorsResult = validation(formData);
				const customErrors =
					customErrorsResult instanceof Promise ? await customErrorsResult : customErrorsResult;
				Object.keys(customErrors).forEach((fieldName) => {
					newErrors[fieldName] = customErrors[fieldName];
				});
			}
		}

		return newErrors;
	};

	const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
		e.preventDefault();
		setSubmitting(true);
		setErrors({});

		try {
			const validationErrors = await validateFormFields();
			if (Object.keys(validationErrors).length > 0) {
				setErrors(validationErrors);
				setSubmitting(false);
				return;
			}

			// Transform data if needed
			const dataToSubmit = transformFormData ? transformFormData(formData) : formData;

			// Submit to API
			const apiResult =
				mode === "add"
					? await api.post(`${endpoint}/`, dataToSubmit, token)
					: await api.put(`${endpoint}/${effectiveData.id}`, dataToSubmit, token);

			// Handle success
			if (mode === "add") {
				onSuccess?.(apiResult);
			}

			// Update UI
			if (mode === "add" || mode === "edit") {
				handleHideImmediate();
			} else {
				Object.assign(effectiveData, apiResult);
				setEffectiveData({ ...effectiveData });
				handleEditToView();
			}
		} catch (err: any) {
			const errorMessage = `Failed to ${mode === "add" ? "create" : "update"} 
			${itemName.toLowerCase()} due to the following error: ${err.message}`;
			setErrors({
				submit: errorMessage,
			});
		} finally {
			setSubmitting(false);
		}
	};

	const getModalId = (): string => {
		if (isEditing) {
			return `modal-edit-${itemName.toLowerCase()}`;
		} else {
			return `modal-view-${itemName.toLowerCase()}`;
		}
	};

	const renderHeader = (): JSX.Element => {
		let icon: string, text: string;
		if (mode === "add") {
			icon = "bi bi-plus-circle";
			text = `Add New ${itemName}`;
		} else if (mode === "edit" || isEditing) {
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

	const renderBodyContent = (): JSX.Element => {
		if (loading) {
			return (
				<div
					className="d-flex justify-content-center align-items-center py-5 modal-content-animated"
					style={{ height: containerHeight }}
				>
					<Spinner animation="border" variant="primary" />
					<span className="ms-3">Loading {itemName.toLowerCase()}...</span>
				</div>
			);
		}

		const currentFields = getCurrentFields();
		const currentAdditionalFields = getCurrentAdditionalFields();
		const formFields = filterConditionalFields(currentFields.form);

		const renderContentInner = () => (
			<div className={`modal-content-visible`}>
				{isEditing ? (
					<div>
						{errors.submit && <Alert variant="danger">{errors.submit}</Alert>}
						<div>
							{formFields.map((item: FormField | FormField[], index: number) => (
								<div key={`form-field-${index}`}>{renderFieldGroup(item, index, true)}</div>
							))}
						</div>
					</div>
				) : (
					<div>
						{currentFields.view.length > 0 && (
							<Card>
								<Card.Body>
									<div>
										{currentFields.view.map((item: ViewField | ViewField[], index: number) => (
											<div key={`view-field-${index}`}>
												{renderFieldGroup(item, index, false)}
											</div>
										))}
									</div>
								</Card.Body>
							</Card>
						)}

						{currentAdditionalFields && currentAdditionalFields.length > 0 && (
							<div className="outside-card-content mt-3">
								{currentAdditionalFields.map((item: ViewField, index: number) => (
									<div key={`outside-field-${index}`} className="mb-3">
										{renderViewElement(item, effectiveData, getModalId())}
									</div>
								))}
							</div>
						)}
					</div>
				)}
			</div>
		);

		return (
			<div className="modal-content-animated" style={{ height: containerHeight }}>
				<div className="modal-content-animated-inner">
					<div ref={contentRef}>{renderContentInner()}</div>
				</div>
			</div>
		);
	};

	const renderBody = (): JSX.Element => {
		if (hasTabs) {
			return (
				<>
					<div className="custom-tab-nav">
						{tabs.map((tab: TabConfig): JSX.Element => {
							const tabTitle = typeof tab.title === "function" ? tab.title(effectiveData) : tab.title;

							return (
								<button
									key={tab.key}
									type="button"
									className={`custom-tab-button ${activeTab === tab.key ? "active" : ""}`}
									onClick={() => handleTabChange(tab.key)}
								>
									{tabTitle}
								</button>
							);
						})}
					</div>
					<div className="custom-tab-content">{renderBodyContent()}</div>
				</>
			);
		}
		return renderBodyContent();
	};

	const renderFooter = (): JSX.Element => {
		if (isEditing) {
			if (mode === "add") {
				return (
					<Modal.Footer>
						<div className="d-flex flex-column w-100 gap-2">
							<div className="modal-buttons-container">
								<ActionButton
									id="cancel-button"
									variant="secondary"
									onClick={handleHideImmediate}
									defaultText="Cancel"
									fullWidth={false}
								/>
								<ActionButton
									id="confirm-button"
									type="submit"
									disabled={submitting || loading}
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
							{id ? (
								<div className="modal-buttons-container">
									<ActionButton
										id="cancel-button"
										variant="secondary"
										onClick={mode === "edit" ? handleHideImmediate : handleEditToView}
										defaultText={mode === "edit" ? "Close" : "Cancel"}
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
							) : (
								<>
									<div className="modal-buttons-container">
										<ActionButton
											variant="danger"
											onClick={handleDeleteClick}
											className="me-auto"
											defaultText="Delete"
											defaultIcon="bi bi-trash"
											fullWidth={false}
											disabled={typeof id === "number"}
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
									<div className="modal-buttons-container">
										<ActionButton
											id="cancel-button"
											variant="secondary"
											onClick={mode === "edit" ? handleHideImmediate : handleEditToView}
											defaultText={mode === "edit" ? "Close" : "Cancel"}
											fullWidth={false}
										/>
									</div>
								</>
							)}
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
							onClick={handleHideImmediate}
							defaultText="Close"
							fullWidth={false}
						/>
						<ActionButton
							id="edit-button"
							variant="primary"
							onClick={handleEdit}
							defaultText="Edit"
							fullWidth={false}
							disabled={loading}
						/>
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
				onHide={handleCloseWithConfirmation}
				size={size}
				centered={true}
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

export interface DataModalProps {
	show: boolean;
	onHide: () => void;
	submode?: "view" | "edit" | "add";
	data?: any;
	id?: number | null;
	onSuccess?: (data: any) => void;
	onDelete?: ((item: any) => Promise<void>) | null;
	size?: "sm" | "lg" | "xl";
}
