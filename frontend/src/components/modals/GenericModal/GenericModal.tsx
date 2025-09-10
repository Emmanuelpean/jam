import React, { JSX, ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";
import { Alert, Card, Form, Modal, Spinner } from "react-bootstrap";
import { useAuth } from "../../../contexts/AuthContext";
import "./GenericModal.css";
import { renderViewElement } from "../../rendering/view/ViewRenders";
import { Errors, renderFormField } from "../../rendering/widgets/WidgetRenders";
import { ActionButton } from "../../rendering/form/ActionButton";
import { api } from "../../../services/Api";
import useGenericAlert from "../../../hooks/useGenericAlert";
import AlertModal from "../AlertModal";
import { areSame, findByKey, flattenArray } from "../../../utils/Utils";
import { renderViewField, ViewField } from "../../rendering/view/ModalFieldRenders";
import { FormField } from "../../rendering/form/FormRenders";
import { SyntheticEvent } from "../../rendering/widgets/WidgetRenders";

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
	submode?: "view" | "edit" | "add";
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
	submode = "view",
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
	const hasTabs = tabs && tabs.length > 0 && tabs[0];

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
		// Load the data
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

	// ------------------------------------------------ DATA POPULATING ------------------------------------------------

	const getCurrentTab = (): TabConfig | null | undefined => {
		if (!hasTabs) return null;
		return findByKey(tabs, activeTab) || tabs[0];
	};

	const getEffectiveProps = (): ModalProps => {
		// Get the current tab's properties
		const currentTab = getCurrentTab();
		const baseProps = {
			submode,
			fields: fields as { view: ViewField[]; form: FormField[] },
			data: effectiveData,
			additionalFields,
			endpoint,
			onSuccess,
			validation,
			transformFormData,
			onFormDataChange,
			onDelete,
		};

		if (!currentTab) {
			return baseProps;
		}

		// Override with tab-specific fields
		return {
			...baseProps,
			fields: currentTab.fields,
			additionalFields: currentTab.additionalFields || additionalFields,
		};
	};

	useEffect(() => {
		// Initialize the modal's state when it first becomes visible or when data loads
		if (show && (!previousShow.current || (effectiveData && Object.keys(formData).length === 0))) {
			const effectiveProps = getEffectiveProps();

			if (effectiveProps.submode === "add") {
				setFormData({});
				setOriginalFormData({});
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
			if (hasTabs && !previousShow.current) {
				setActiveTab(defaultActiveTab || tabs[0]!.key);
			}
		}
		previousShow.current = show;
	}, [show, data, submode, tabs, defaultActiveTab, effectiveData]);

	const handleTabChange = async (tabKey: string): Promise<void> => {
		if (hasTabs) {
			if (hasUnsavedChanges()) {
				try {
					await showDelete({
						title: "Unsaved Changes",
						message: "You have unsaved changes. Are you sure you want to switch tabs without saving?",
						confirmText: "Switch without saving",
						cancelText: "Cancel",
					});
				} catch (error) {
					// User cancelled, don't switch tabs
					return;
				}
			}

			setActiveTab(tabKey);
			const effectiveProps = getEffectiveProps();

			const newData = effectiveProps.data || data;

			if (effectiveProps.submode === "add") {
				setFormData({ ...newData });
				setOriginalFormData({ ...newData });
				setIsEditing(true);
			} else if (effectiveProps.submode === "edit") {
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
	};

	useEffect(() => {
		// Allow to have dynamic form fields
		const effectiveProps = getEffectiveProps();
		if (effectiveProps.onFormDataChange && isEditing) {
			effectiveProps.onFormDataChange(formData);
		}
	}, [formData, isEditing, activeTab]);

	// ---------------------------------------------------- CLOSING ----------------------------------------------------

	const hasUnsavedChanges = (): boolean => {
		// Check if there are any changes in the form data
		if (!isEditing) return false;
		const keys: string[] = Object.keys(formData);
		return keys.some((key: string) => {
			const currentValue: any = formData[key as keyof typeof formData];
			const originalValue: any = originalFormData[key as keyof typeof originalFormData];
			return areSame(currentValue, originalValue);
		});
	};

	const handleCloseWithConfirmation = async () => {
		// Check if there are any unsaved changes before closing the modal
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
		// Change the mode from edit to view
		setIsEditing(false);
		const effectiveProps = getEffectiveProps();
		setFormData({ ...effectiveProps.data });
		setOriginalFormData({ ...effectiveProps.data });
		setErrors({});
	};

	const handleEdit = () => {
		// Change the mode from view to edit
		setIsEditing(true);
		const effectiveProps = getEffectiveProps();
		setFormData({ ...effectiveProps.data });
		setOriginalFormData({ ...effectiveProps.data });
	};

	// ----------------------------------------------------- LAYOUT ----------------------------------------------------

	useLayoutEffect(() => {
		if (!contentRef.current) return;

		const updateHeight = (): void => {
			if (contentRef.current?.scrollHeight) {
				setContainerHeight(String(Number(contentRef.current.scrollHeight) + 1) + "px");
			}
		};

		// Initial height calculation
		updateHeight();

		// Create ResizeObserver to watch for content size changes
		const resizeObserver = new ResizeObserver(() => {
			updateHeight();
		});

		// Observe the content element
		resizeObserver.observe(contentRef.current);

		// Also observe all child elements that might change size
		const childElements = contentRef.current.querySelectorAll("*");
		childElements.forEach((el: Element) => {
			resizeObserver.observe(el);
		});

		// Cleanup
		return () => {
			resizeObserver.disconnect();
		};
	}, [isEditing, activeTab, fields, additionalFields, effectiveData]);

	// ------------------------------------------------- MODAL CONTENT -------------------------------------------------

	const getCurrentFields = (): ViewFields | FormFields => {
		const effectiveProps: ModalProps = getEffectiveProps();
		if (isEditing) {
			return effectiveProps.fields.form;
		} else {
			return effectiveProps.fields.view;
		}
	};

	const getCurrentData = (): any => {
		const effectiveProps = getEffectiveProps();
		return effectiveProps.data;
	};

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
				const hasElementsUnderneath = index < currentFields.length - 1;

				return (
					<div className={hasElementsUnderneath ? "mb-3" : ""}>
						{renderViewField(firstItem as ViewField, getCurrentData(), getModalId())}
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
						("name" in field ? field.name : null) || // TODO remove name and use key instead
						`field_${index}_${fieldIndex}`;

					return (
						<div key={fieldKey} className={columnClass}>
							{isFormMode
								? renderFormField(
										field as FormField,
										formData,
										//@ts-ignore
										handleChange,
										errors,
									)
								: renderViewField(field as ViewField, getCurrentData(), getModalId())}
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
		// TODO this shouldn't reload the page
		const effectiveProps = getEffectiveProps();
		try {
			await handleDelete(effectiveProps.data);
			if (onDelete) {
				await onDelete(effectiveProps.data);
			}
			handleHideImmediate();
		} catch (error) {}
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

	const validateFormFields = async (): Promise<{}> => {
		const newErrors: Errors = {};
		const allFields = flattenArray(getCurrentFields());
		const effectiveProps = getEffectiveProps();

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

		// 3) Custom entry validation (e.g. check that the entry does not already exist, only run if no previous errors)
		if (effectiveProps.validation && Object.keys(newErrors).length === 0) {
			if (typeof effectiveProps.validation === "function") {
				const customErrorsResult = effectiveProps.validation(formData);
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
		e.preventDefault(); // Prevent default form submission behavior (i.e. page reload)
		const effectiveProps: ModalProps = getEffectiveProps();
		setSubmitting(true);
		setErrors({});
		try {
			const validationErrors = await validateFormFields();
			if (Object.keys(validationErrors).length > 0) {
				setErrors(validationErrors);
				setSubmitting(false);
				return;
			} else {
				// Transform data if needed
				const dataToSubmit = effectiveProps.transformFormData
					? effectiveProps.transformFormData(formData)
					: formData;

				// Submit to API
				const apiResult =
					effectiveProps.submode === "add"
						? await api.post(`${endpoint}/`, dataToSubmit, token)
						: await api.put(`${endpoint}/${getCurrentData().id}`, dataToSubmit, token);

				// Handle success
				if (effectiveProps.submode === "add") {
					effectiveProps.onSuccess?.(apiResult);
				}

				// Update UI
				if (effectiveProps.submode === "add" || effectiveProps.submode === "edit") {
					handleHideImmediate();
				} else {
					Object.assign(getCurrentData(), apiResult);
					handleEditToView();
				}
			}
		} catch (err: any) {
			const errorMessage = `Failed to ${effectiveProps.submode === "add" ? "create" : "update"} 
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
		const effectiveProps = getEffectiveProps();
		let icon: string, text: string;
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

		const effectiveProps = getEffectiveProps();
		const viewFields = effectiveProps.fields.view;
		const formFields = effectiveProps.fields.form;
		const additionalFields = effectiveProps.additionalFields;

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
						{viewFields.length > 0 && (
							<Card>
								<Card.Body>
									<div>
										{viewFields.map((item: ViewField | ViewField[], index: number) => (
											<div key={`view-field-${index}`}>
												{renderFieldGroup(item, index, false)}
											</div>
										))}
									</div>
								</Card.Body>
							</Card>
						)}

						{additionalFields && additionalFields.length > 0 && (
							<div className="outside-card-content mt-3">
								{additionalFields.map((item: ViewField, index: number) => (
									<div key={`outside-field-${index}`} className="mb-3">
										{renderViewElement(item, getCurrentData(), getModalId())}
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
							const tabTitle = typeof tab.title === "function" ? tab.title(getCurrentData()) : tab.title;

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
										onClick={
											effectiveProps.submode === "edit" ? handleHideImmediate : handleEditToView
										}
										defaultText={effectiveProps.submode === "edit" ? "Close" : "Cancel"}
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
											onClick={
												effectiveProps.submode === "edit"
													? handleHideImmediate
													: handleEditToView
											}
											defaultText={effectiveProps.submode === "edit" ? "Close" : "Cancel"}
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
