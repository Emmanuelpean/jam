import React, { JSX, ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";
import { Alert, Card, Form, Modal } from "react-bootstrap";
import { useAuth } from "../../../contexts/AuthContext";
import { DataContextValue, endpointToEntityType, EntityType, useDataContext } from "../../../contexts/DataContext";
import "./DataModal.css";
import { Errors, FormField, SyntheticEvent } from "../../rendering/widgets/WidgetRenders";
import { ActionButton } from "../../rendering/form/ActionButton";
import useGenericAlert from "../../../hooks/useGenericAlert";
import AlertModal from "../AlertModal";
import { areDifferent, findItemByKey, flattenArray, getColumnClass } from "../../../utils/Utils";
import { ModalViewField, renderModalViewField } from "../../rendering/view/ModalFields";
import { ModalFormField } from "../../rendering/form/FormRenders";
import { useDeleteHandler } from "../../../utils/DeleteHandler";

export type Field = ModalViewField | ModalFormField;
export type Fields = (Field | Field[])[];

export interface TabConfig {
	key: string;
	title: string | JSX.Element | ((data: any) => ReactNode);
	fields: { view: Fields; form: Fields };
	additionalFields?: ModalViewField[];
}

export interface GenericModalProps {
	mode?: "view" | "edit" | "add" | "import"; // modal mode
	fields?: { view: Fields; form: Fields }; // fields to display
	data?: any; // data to populate the fields (required for import mode)
	validation?: ((data: any) => any) | null; // custom validation method before submit
	transformFormData?: ((data: any) => any) | null; // custom data transformation before submit
	onFormDataChange?: ((data: any) => void) | null;
	additionalFields?: ModalViewField[]; // additional fields displayed outside the card in view mode
	show: boolean; // whether to show the modal
	onHide: () => void; // called to hide the modal
	itemName?: string; // name of the item being managed, used in titles and messages
	size?: "sm" | "lg" | "xl"; // modal size
	tabs?: TabConfig[] | null; // optional tabs configuration
	defaultActiveTab?: string | null; // default active tab key
	endpoint: string; // API endpoint for CRUD operations
	onSuccess?: (data: any) => void; // called when an entry is successfully added/modified
	warningMessage?: string | ReactNode; // optional warning message to display
	warningVariant?: "warning" | "danger" | "info" | "primary" | "secondary" | "success";
}

export interface ValidationErrors {
	[key: string]: string;
}

const DataModal = ({
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
	endpoint,
	validation = null,
	transformFormData = null,
	onSuccess,
	warningMessage,
	warningVariant = "warning",
}: GenericModalProps) => {
	const hasTabs = tabs && tabs.length > 0;

	const dataContext: DataContextValue = useDataContext();
	const entityType: EntityType = endpointToEntityType(endpoint)!;
	const [effectiveData, setEffectiveData] = useState(data);
	const [formData, setFormData] = useState<Record<string, any>>({});
	const [originalFormData, setOriginalFormData] = useState<Record<string, any>>({});
	const [submitting, setSubmitting] = useState(false);
	const [errors, setErrors] = useState<Errors>({});
	const [isEditing, setIsEditing] = useState(false);
	const { currentUser } = useAuth();
	const [activeTab, setActiveTab] = useState<string | null>(() => {
		if (hasTabs) {
			return defaultActiveTab || tabs[0]!.key;
		}
		return null;
	});
	const [containerHeight, setContainerHeight] = useState("auto");
	const contentRef = useRef<HTMLDivElement>(null);
	const { alertState, showDelete, showError, hideAlert } = useGenericAlert();

	// -------------------------------------------------- DATA LOADING -------------------------------------------------

	useEffect(() => {
		setEffectiveData(data);
	}, [data]);

	// ------------------------------------------------ MODAL STATE INIT ------------------------------------------------

	const getCurrentTabConfig = (): TabConfig | null => {
		if (!hasTabs) return null;
		return findItemByKey(tabs, activeTab) || tabs[0]!;
	};

	const isViewField = (field: Field): field is ModalViewField => {
		return !("name" in field) || "render" in field || "isTitle" in field;
	};

	const getCurrentFields = (): { view: Fields; form: Fields } => {
		const currentTab: TabConfig | null = getCurrentTabConfig();
		if (!currentTab) {
			return {
				view: filterConditionalFields(fields!.view),
				form: filterConditionalFields(fields!.form),
			};
		} else {
			return {
				view: filterConditionalFields(currentTab.fields.view),
				form: filterConditionalFields(currentTab.fields.form),
			};
		}
	};

	const getAllFields = (): { view: Fields; form: Fields } => {
		if (!hasTabs || !tabs) {
			return {
				form: filterConditionalFields(fields!.form),
				view: filterConditionalFields(fields!.view),
			};
		} else {
			return {
				form: tabs.flatMap((tab: TabConfig) => filterConditionalFields(tab.fields.form)),
				view: tabs.flatMap((tab: TabConfig) => filterConditionalFields(tab.fields.view)),
			};
		}
	};

	const getCurrentAdditionalFields = (): ModalViewField[] => {
		const currentTab = getCurrentTabConfig();
		return currentTab?.additionalFields || additionalFields;
	};

	useEffect(() => {
		// Initialize modal state when it becomes visible or data changes
		if (!show) return;
		if (mode === "add" || mode === "edit" || mode === "import") {
			setFormData({ ...data });
			setOriginalFormData({ ...data });
			setIsEditing(true);
		} else if (mode === "view") {
			setFormData({ ...data });
			setOriginalFormData({ ...data });
			setIsEditing(false);
		}
		setErrors({});

		// Reset active tab only when modal first opens
		if (hasTabs) {
			setActiveTab(defaultActiveTab || tabs[0]!.key);
		}
	}, [show, mode, defaultActiveTab]);

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
			const confirmed = await showDelete({
				title: "Unsaved Changes",
				message: "You have unsaved changes. Are you sure you want to close without saving?",
				confirmText: "Close without saving",
				cancelText: "Cancel",
			});
			if (!confirmed) {
				return false;
			} else {
				handleHideImmediate();
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
	}, [isEditing, activeTab, effectiveData, show]);

	// ------------------------------------------------- MODAL CONTENT -------------------------------------------------

	const renderFieldGroup = (item: Field | Field[], index: number, isFormMode = true) => {
		let itemList: Field[];
		if (Array.isArray(item)) {
			itemList = item;
		} else {
			itemList = [item];
		}

		// Handle title fields in view mode
		if (!isEditing && itemList.length === 1) {
			const firstItem = itemList[0];
			if (firstItem && "isTitle" in firstItem && firstItem.isTitle) {
				const currentFields = getCurrentFields();
				const fieldsToCheck = isFormMode ? currentFields.form : currentFields.view;
				const hasElementsUnderneath = index < fieldsToCheck.length - 1;

				return (
					<div className={hasElementsUnderneath ? "mb-3" : ""} key={index}>
						{renderModalViewField(firstItem as ModalViewField, effectiveData, getModalId())}
					</div>
				);
			}
		}

		const columnClass = getColumnClass(itemList.length);

		return (
			<div key={index} className="row mb-3" style={{ paddingRight: "0.3rem", paddingLeft: "0.3rem" }}>
				{itemList.map((field: Field, fieldIndex: number) => {
					const fieldKey =
						("key" in field ? field.key : null) ||
						("name" in field ? field.name : null) ||
						`field_${index}_${fieldIndex}`;

					// Always render based on field type, not mode
					return (
						<div key={fieldKey} className={columnClass}>
							{isViewField(field)
								? renderModalViewField(field as ModalViewField, effectiveData, getModalId())
								: FormField(field as ModalFormField, formData, handleChange, errors, currentUser)}
						</div>
					);
				})}
			</div>
		);
	};

	// ----------------------------------------------------- DELETE ----------------------------------------------------

	const handleDelete = useDeleteHandler({
		entityType: entityType,
		showDelete: showDelete,
		showError: showError,
		itemType: itemName,
	});

	const handleDeleteClick = async () => {
		const confirm = await handleDelete(effectiveData);
		if (confirm) {
			handleHideImmediate();
		}
	};

	const handleChange = (e: SyntheticEvent) => {
		const { name, type, checked, value } = e.target;
		setFormData((prev) => ({
			...prev,
			[name]: type === "checkbox" ? checked : value,
		}));
		if (errors[name]) {
			setErrors((prev) => ({ ...prev, [name]: "" }));
		}
	};

	const filterConditionalFields = <T extends Field>(fieldsToFilter: (T | T[])[]): (T | T[])[] => {
		return fieldsToFilter
			.map((item) => {
				if (Array.isArray(item)) {
					const filteredArray = item.filter((field) => {
						if (!field.displayCondition) {
							return true;
						} else {
							return field.displayCondition(formData);
						}
					});
					return filteredArray.length > 0 ? filteredArray : null;
				} else {
					if (!item.displayCondition) {
						return item;
					} else {
						return item.displayCondition(formData) ? item : null;
					}
				}
			})
			.filter((item) => item !== null) as (T | T[])[];
	};

	const validateFormFields = async (): Promise<Errors> => {
		const newErrors: Errors = {};
		const currentFields = getAllFields();
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

		// Switch to the tab containing the first error
		if (hasTabs && tabs) {
			for (const tab of tabs) {
				const tabFields = flattenArray(filterConditionalFields(tab.fields.form));
				if (tabFields.some((field: ModalFormField) => newErrors[field.name])) {
					setActiveTab(tab.key);
					break;
				}
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
				mode === "add" || mode == "import"
					? await dataContext.addEntity(entityType, dataToSubmit)
					: await dataContext.updateEntity(entityType, data.id, dataToSubmit);
			if (mode === "add" || mode === "edit" || mode == "import") {
				handleHideImmediate();
			} else {
				setEffectiveData(apiResult);
				handleEditToView();
			}
			if (mode === "import" && onSuccess) {
				onSuccess(dataToSubmit);
			} else if (onSuccess) {
				onSuccess(apiResult);
			}
		} catch (err: any) {
			const errorMessage = `Failed to ${mode === "add" || mode === "import" ? "create" : "update"} 
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
			if (mode === "import") {
				return `modal-import-${itemName.toLowerCase()}`;
			}
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
		} else if (mode === "import") {
			icon = "bi bi-download";
			text = `Import ${itemName}`;
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
					<span style={{ display: "flex", alignItems: "center" }}>
						{icon && <i className={`${icon} me-2`} style={{ fontSize: "1.05em" }} />}
						<span>{text}</span>
					</span>
				</Modal.Title>
			</Modal.Header>
		);
	};

	const renderBodyContent = (): JSX.Element => {
		const currentFields = getCurrentFields();
		const currentAdditionalFields = getCurrentAdditionalFields();

		const renderContentInner = () => (
			<div className={`modal-content-visible`}>
				{warningMessage && (
					<Alert variant={warningVariant} className="mb-3">
						{warningMessage}
					</Alert>
				)}
				{isEditing ? (
					<div>
						{errors.submit && <Alert variant="danger">{errors.submit}</Alert>}
						<div>
							{currentFields.form.map((item, index: number) => (
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
										{currentFields.view.map((item, index: number) => (
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
								{currentAdditionalFields.map((item: ModalViewField, index: number) => (
									<div key={`outside-field-${index}`} className="mb-3">
										{renderModalViewField(item, effectiveData, getModalId())}
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
									onClick={() => setActiveTab(tab.key)}
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
									id={getModalId() + "-cancel-button"}
									variant="secondary"
									onClick={handleHideImmediate}
									defaultText="Cancel"
									fullWidth={false}
								/>
								<ActionButton
									id={getModalId() + "-confirm-button"}
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
			} else if (mode === "import") {
				return (
					<Modal.Footer>
						<div className="d-flex flex-column w-100 gap-2">
							<div className="modal-buttons-container">
								<ActionButton
									id={getModalId() + "-delete-button"}
									variant="danger"
									onClick={handleDeleteClick}
									className="me-auto"
									defaultText="Delete"
									defaultIcon="bi bi-trash"
								/>
								<ActionButton
									id={getModalId() + "-import-button"}
									type="submit"
									disabled={submitting}
									loading={submitting}
									loadingText="Importing..."
									defaultText="Import"
									defaultIcon="bi bi-download"
									fullWidth={false}
								/>
							</div>
							<div className="modal-buttons-container">
								<ActionButton
									id={getModalId() + "-cancel-button"}
									variant="secondary"
									onClick={handleHideImmediate}
									defaultText="Cancel"
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
							<>
								<div className="modal-buttons-container">
									<ActionButton
										id={getModalId() + "-delete-button"}
										variant="danger"
										onClick={handleDeleteClick}
										className="me-auto"
										defaultText="Delete"
										defaultIcon="bi bi-trash"
										fullWidth={false}
									/>

									<ActionButton
										id={getModalId() + "-confirm-button"}
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
										id={getModalId() + "-cancel-button"}
										variant="secondary"
										onClick={mode === "edit" ? handleHideImmediate : handleEditToView}
										defaultText={mode === "edit" ? "Close" : "Cancel"}
										fullWidth={false}
									/>
								</div>
							</>
						</div>
					</Modal.Footer>
				);
			}
		} else {
			return (
				<Modal.Footer>
					<div className="modal-buttons-container">
						<ActionButton
							id={getModalId() + "-cancel-button"}
							variant="secondary"
							onClick={handleHideImmediate}
							defaultText="Close"
							fullWidth={false}
						/>
						<ActionButton
							id={getModalId() + "-edit-button"}
							variant="primary"
							onClick={handleEdit}
							defaultText="Edit"
							fullWidth={false}
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
				key={getModalId()}
			>
				{isEditing ? <Form onSubmit={handleSubmit}>{modalContent}</Form> : modalContent}
			</Modal>
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};

export default DataModal;

export interface DataModalProps {
	show: boolean;
	onHide: () => void;
	submode?: "view" | "edit" | "add" | "import";
	data?: any;
	onSuccess?: (data: any) => void;
	onDelete?: (id: number | string) => void;
	size?: "sm" | "lg" | "xl";
}
