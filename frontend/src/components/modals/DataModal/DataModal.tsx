import React, {
	forwardRef,
	JSX,
	ReactNode,
	useEffect,
	useImperativeHandle,
	useLayoutEffect,
	useRef,
	useState,
} from "react";
import { Alert, Card, Form, Modal } from "react-bootstrap";
import { useAuth } from "../../../contexts/AuthContext";
import {
	DataContextValue,
	endpointToEntityType,
	EntityType,
	JamData,
	useDataContext,
} from "../../../contexts/DataContext";
import { Errors, FormField, SyntheticEvent } from "../../rendering/widgets/WidgetRenders";
import { ActionButton } from "../../rendering/form/ActionButton";
import { areDifferent, findItemByKey, flattenArray, getColumnClass, normaliseArray } from "../../../utils/Utils";
import { ModalViewField, renderModalViewField } from "../../rendering/view/ModalFields";
import { ModalFormField } from "../../rendering/form/FormRenders";
import { useActiveHandler, useDeleteHandler } from "../../../utils/DeleteHandler";
import { useAlert } from "../../../contexts/AlertContext";
import "./DataModal.css";
import { ApiResponse } from "../../../services/api/Base";

export type Field = ModalViewField | ModalFormField;
export type Fields = (Field | Field[])[];

export interface TabConfig {
	key: string;
	title: string | JSX.Element | ((data: any) => ReactNode);
	fields: { view: Fields; form: Fields };
	additionalFields?: ModalViewField[];
}

export interface WarningConfig {
	key?: string;
	message: ReactNode;
	variant?: "warning" | "danger" | "info" | "primary" | "secondary" | "success";
}

export interface DataModalProps {
	mode?: "view" | "edit" | "add" | "import"; // modal mode
	fields?: { view: Fields; form: Fields } | ((data: any, mode: string) => { view: Fields; form: Fields }); // fields to display
	data?: any; // data to populate the fields (required for import mode)
	validation?: ((data: any) => any) | null; // custom validation method before submit
	transformFormData?: ((data: any) => any) | null; // custom data transformation before submit
	transformInputData?: ((data: any) => any) | null; // custom data transformation when loading data into the form
	additionalFields?: ModalViewField[]; // additional fields displayed outside the card in view mode
	itemName?: string; // name of the item being managed, used in titles and messages
	size?: "sm" | "lg" | "xl"; // modal size
	tabs?: TabConfig[] | null; // optional tabs configuration
	defaultActiveTab?: string | null; // default active tab key
	endpoint: string; // API endpoint for CRUD operations
	onSuccess?: (data: any, onSuccess?: (newData: any) => void) => void; // called when an entry is successfully added/modified
	onDelete?: () => void; // called when an entry is successfully deleted
	warningMessage?: (data: any) => WarningConfig[] | null; // optional warning message to display
	canEdit?: boolean; // Controls edit button and edit mode access
}

export interface ValidationErrors {
	[key: string]: string;
}

export interface DataModalHandle {
	showView: (data: any) => void;
	showEdit: (data: any) => void;
	showAdd: (data: any) => void;
	showImport: (data: any) => void;
	hide: () => void;
}

const DataModal = forwardRef<DataModalHandle, DataModalProps>(
	(
		{
			fields,
			itemName = "Entry",
			size = "lg",
			tabs = null,
			defaultActiveTab = null,
			additionalFields = [],
			endpoint,
			validation = null,
			transformFormData = null,
			transformInputData = null,
			onSuccess,
			onDelete,
			warningMessage,
			canEdit = true,
		}: DataModalProps,
		ref,
	) => {
		const hasTabs = tabs && tabs.length > 0;

		const [internalShow, setInternalShow] = useState(false);
		useImperativeHandle(ref, () => ({
			showView: (data: JamData) => {
				transformInputData ? setEffectiveData(transformInputData(data)) : setEffectiveData(data);
				setMode("view");
				setInternalShow(true);
			},
			showEdit: (data: JamData) => {
				transformInputData ? setEffectiveData(transformInputData(data)) : setEffectiveData(data);
				setMode("edit");
				setInternalShow(true);
			},
			showAdd: (data: JamData, successCallback?: (newData: JamData) => void) => {
				transformInputData ? setEffectiveData(transformInputData(data)) : setEffectiveData(data);
				setMode("add");
				setOnSuccessCallback(() => successCallback || null);
				setInternalShow(true);
			},
			showImport: (data: JamData) => {
				transformInputData ? setEffectiveData(transformInputData(data)) : setEffectiveData(data);
				setMode("import");
				setInternalShow(true);
			},
			hide: () => setInternalShow(false),
		}));

		const [onSuccessCallback, setOnSuccessCallback] = useState<((data: any) => void) | null>(null);
		const [mode, setMode] = useState<"view" | "edit" | "add" | "import">("view");
		const dataContext: DataContextValue = useDataContext();
		const entityType: EntityType = endpointToEntityType(endpoint)!;
		const [effectiveData, setEffectiveData] = useState<any>(null);
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
		const { showDelete } = useAlert();

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

			// Handle fields as function or object
			const fieldsConfig = typeof fields === "function" ? fields(effectiveData, mode) : fields;

			if (!currentTab) {
				return {
					view: filterConditionalFields(fieldsConfig!.view),
					form: filterConditionalFields(fieldsConfig!.form),
				};
			} else {
				return {
					view: filterConditionalFields(currentTab.fields.view),
					form: filterConditionalFields(currentTab.fields.form),
				};
			}
		};

		const getAllFields = (): { view: Fields; form: Fields } => {
			const fieldsConfig = typeof fields === "function" ? fields(effectiveData, mode) : fields;

			if (!hasTabs || !tabs) {
				return {
					form: filterConditionalFields(fieldsConfig!.form),
					view: filterConditionalFields(fieldsConfig!.view),
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
			if (!internalShow) return;
			if (mode === "add" || mode === "edit" || mode === "import") {
				setFormData({ ...effectiveData });
				setOriginalFormData({ ...effectiveData });
				setIsEditing(true);
			} else if (mode === "view") {
				setFormData({ ...effectiveData });
				setOriginalFormData({ ...effectiveData });
				setIsEditing(false);
			}
			setErrors({});

			// Reset active tab only when modal first opens
			if (hasTabs) {
				setActiveTab(defaultActiveTab || tabs[0]!.key);
			}
		}, [internalShow, mode, defaultActiveTab, effectiveData]);

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
			setInternalShow(false);
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
		}, [isEditing, activeTab, effectiveData, internalShow]);

		// ------------------------------------------------- MODAL CONTENT -------------------------------------------------

		const renderFieldGroup = (item: Field | Field[], index: number, isFormMode = true): JSX.Element => {
			const itemList: Field[] = normaliseArray(item);

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

		const handleDelete = useDeleteHandler(entityType, null, itemName);
		const handleDeActivate = useActiveHandler(entityType, null, itemName);

		const handleDeleteClick = async () => {
			if (mode === "import") {
				const confirm: boolean = await handleDeActivate(effectiveData);
				if (confirm) {
					onDelete?.();
					handleHideImmediate();
				}
			} else {
				const confirm: boolean = await handleDelete(effectiveData);
				if (confirm) {
					onDelete?.();
					handleHideImmediate();
				}
			}
		};

		const handleChange = (e: SyntheticEvent): void => {
			const { name, type, checked, value } = e.target;
			setFormData((prev) => ({
				...prev,
				[name]: type === "checkbox" ? checked : value,
			}));
			if (errors[name]) {
				setErrors((prev: Errors) => ({ ...prev, [name]: "" }));
			}
		};

		const filterConditionalFields = <T extends Field>(fieldsToFilter: (T | T[])[]): (T | T[])[] => {
			return fieldsToFilter
				.map((item: T | T[]): T | T[] | null => {
					if (Array.isArray(item)) {
						const filteredArray: T[] = item.filter((field: T): boolean => {
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
				.filter((item: T | T[] | null): boolean => item !== null) as (T | T[])[];
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
				const dataToSubmit: any = transformFormData ? transformFormData(formData) : formData;

				// Submit to API
				const apiResult: ApiResponse<JamData> =
					mode === "add"
						? await dataContext.addEntity(entityType, dataToSubmit)
						: await dataContext.updateEntity(entityType, effectiveData.id, dataToSubmit);
				if (mode === "add" || mode === "edit" || mode === "import") {
					handleHideImmediate();
				} else {
					setEffectiveData(apiResult.data);
					handleEditToView();
				}

				requestAnimationFrame(() => {
					requestAnimationFrame(() => {
						// Call callbacks after 2 animation frames - ensures all renders are complete
						if (onSuccess) {
							onSuccess(mode === "import" ? formData : apiResult.data);
						}

						if (onSuccessCallback) {
							onSuccessCallback(apiResult.data);
						}
					});
				});
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
			const warnings = warningMessage ? warningMessage(effectiveData) : null;

			const renderContentInner = () => (
				<div className={`modal-content-visible`}>
					{warnings && warnings.length > 0 && (
						<>
							{warnings.map(({ key, message, variant }, idx) => (
								<Alert key={key ?? idx} variant={variant} className="mb-3">
									{message}
								</Alert>
							))}
						</>
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
										id={tab.key + "-tab"}
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
							{canEdit && (
								<ActionButton
									id={getModalId() + "-edit-button"}
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

		const modalContent: JSX.Element = (
			<>
				{renderHeader()}
				<Modal.Body>{renderBody()}</Modal.Body>
				{renderFooter()}
			</>
		);

		return (
			<>
				<Modal
					show={internalShow}
					onHide={handleCloseWithConfirmation}
					size={size}
					centered={true}
					backdrop={true}
					keyboard={true}
					id={getModalId()}
				>
					{isEditing ? <Form onSubmit={handleSubmit}>{modalContent}</Form> : modalContent}
				</Modal>
			</>
		);
	},
);

export default DataModal;

export interface JamDataModalProps {
	onSuccess?: (data: any) => void;
	size?: "sm" | "lg" | "xl";
	canEdit?: boolean;
}
