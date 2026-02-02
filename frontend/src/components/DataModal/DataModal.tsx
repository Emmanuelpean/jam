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
import { useAuth } from "../../contexts/AuthContext";
import {
	DataContextValue,
	EntityType,
	entityTypeToGenericName,
	JamData,
	useDataContext,
} from "../../contexts/DataContext";
import { Errors, renderFormField, SyntheticEvent } from "../rendering/widgets/WidgetRenders";
import { ActionButton } from "../rendering/form/ActionButton";
import { areDifferent, findItemByKey, flattenArray, getColumnClass, normaliseArray } from "../../utils/Utils";
import { ModalViewField, renderModalViewField } from "../rendering/view/ModalFields";
import { ModalFormField } from "../rendering/form/FormRenders";
import {
	useActivateEntity,
	useDeactivateEntity,
	useDeactivateEntityConfirm,
	useDeleteEntityConfirm,
} from "../../utils/DeleteHandler";
import { useAlert } from "../../contexts/AlertContext";
import { ApiResponse } from "../../services/api/Base";
import set from "lodash/set";
import get from "lodash/get";
import "./DataModal.scss";
import { toKey } from "../../utils/StringUtils";
import { getModalSize, ModalSize } from "../AlertModal/AlertModal";

export type Field = ModalViewField | ModalFormField;
export type Fields = (Field | Field[])[];

export interface TabConfig {
	key: string;
	title: string | JSX.Element | ((data: any) => ReactNode);
	fields: { view: Fields; form: Fields };
	additionalFields?: ModalViewField[];
}

export interface WarningMessageConfig {
	key?: string;
	message: ReactNode;
	variant?: "warning" | "danger" | "info" | "primary" | "secondary" | "success";
}

export type modalModes = "view" | "edit" | "add" | "import" | "detail";

export interface DataModalProps {
	mode?: modalModes; // modal mode
	fields?: { view: Fields; form: Fields } | ((data: any, mode: string) => { view: Fields; form: Fields }); // fields to display
	data?: any; // data to populate the fields (required for import mode)
	validation?: ((data: any) => any) | null; // custom validation method before submit
	transformFormData?: ((data: any) => any) | null; // custom data transformation before submit
	transformInputData?: ((data: any) => any) | null; // custom data transformation when loading data into the form
	additionalFields?: ModalViewField[]; // additional fields displayed outside the card in view mode
	entityName?: string; // name of the item being managed, used in titles and messages
	size?: ModalSize; // modal size
	tabs?: TabConfig[] | null; // optional tabs configuration
	defaultActiveTab?: string | null; // default active tab key
	entityType: EntityType; // entity type for API operations
	onSuccess?: (data: any, onSuccess?: (newData: any) => void) => void; // called when an entry is successfully added/modified
	onDelete?: () => void; // called when an entry is successfully deleted
	warningMessage?: (data: any) => WarningMessageConfig[] | null; // optional warning message to display
	canEdit?: boolean | ((formData: any) => string); // Controls edit button and edit mode access
	canDelete?: boolean | ((formData: any) => string); // Controls delete button and edit mode access
	showDeactivate?: boolean; // whether to show deactivate items in view mode
}

interface ButtonState {
	disabled: boolean;
	message: string;
}

export interface ValidationErrors {
	[key: string]: string;
}

export interface DataModalHandle {
	showView: (data: JamData) => void;
	showEdit: (data: JamData) => void;
	showAdd: (data: any) => void;
	showImport: (data: any) => void;
}

const DataModal = forwardRef<DataModalHandle, DataModalProps>(
	(
		{
			fields,
			size = "lg",
			tabs = null,
			defaultActiveTab = null,
			additionalFields = [],
			entityType,
			validation = null,
			transformFormData = null,
			transformInputData = null,
			onSuccess,
			onDelete,
			warningMessage,
			canEdit = true,
			canDelete = true,
			showDeactivate = false,
		}: DataModalProps,
		ref
	) => {
		const hasTabs = tabs && tabs.length > 0;

		const [internalShow, setInternalShow] = useState(false);
		const [mode, setMode] = useState<modalModes>("view");
		const [effectiveData, setEffectiveData] = useState<any>(null);
		const [_id, setId] = useState<number | null>(null);
		useImperativeHandle(ref, () => ({
			showView: (data: JamData): void => {
				setId(data.id);
				transformInputData ? setEffectiveData(transformInputData(data)) : setEffectiveData(data);
				setMode("view");
				setInternalShow(true);
			},
			showEdit: (data: JamData): void => {
				setId(data.id);
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
		}));

		const [onSuccessCallback, setOnSuccessCallback] = useState<((data: any) => void) | null>(null);
		const [formData, setFormData] = useState<Record<string, any>>({});
		const [originalFormData, setOriginalFormData] = useState<Record<string, any>>({});
		const [submitting, setSubmitting] = useState<boolean>(false);
		const [activeLoading, setActiveLoading] = useState<boolean>(false);
		const [errors, setErrors] = useState<Errors>({});
		const [isEditing, setIsEditing] = useState<boolean>(false);
		const { currentUser } = useAuth();
		const dataContext: DataContextValue = useDataContext();
		const [activeTab, setActiveTab] = useState<string | null>(() => {
			if (hasTabs) {
				return defaultActiveTab || tabs[0]!.key;
			}
			return null;
		});
		const [containerHeight, setContainerHeight] = useState("auto");
		const contentRef = useRef<HTMLDivElement>(null);
		const { showDelete } = useAlert();
		const entityName: string = entityTypeToGenericName(entityType);

		// useEffect(() => {
		// 	const data = dataContext.getEntityData(entityType).filter((item: JamData): boolean => item.id === id)[0];
		// 	setEffectiveData(data);
		// }, [dataContext.getEntityData(entityType).filter((item: JamData): boolean => item.id === id)[0]]);

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
			if (!internalShow) return;
			if (mode === "add" || mode === "edit" || mode === "import") {
				setFormData({ ...effectiveData });
				setOriginalFormData({ ...effectiveData });
				setIsEditing(true);
			} else if (mode === "view" || mode === "detail") {
				setFormData({ ...effectiveData });
				setOriginalFormData({ ...effectiveData });
				setIsEditing(false);
			}
			setErrors({});

			if (hasTabs) {
				setActiveTab(defaultActiveTab || tabs[0]!.key);
			}
		}, [internalShow, mode, defaultActiveTab, effectiveData]);

		// ---------------------------------------------------- CLOSING ----------------------------------------------------

		const hasUnsavedChanges = (): boolean => {
			if (!isEditing) return false;
			const keys: string[] = Object.keys(formData);
			return keys.some((key: string): boolean => {
				return areDifferent(formData[key], originalFormData[key]);
			});
		};

		const handleCloseWithConfirmation = async (): Promise<false | undefined> => {
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

		const getEditDisabledState = (): ButtonState => {
			if (typeof canEdit === "function") {
				const message = canEdit(formData);
				return { disabled: message !== "", message };
			}
			return { disabled: !canEdit, message: "" };
		};

		const getDeleteDisabledState = (): ButtonState => {
			if (typeof canDelete === "function") {
				const message = canDelete(formData);
				return { disabled: message !== "", message };
			}
			return { disabled: !canDelete, message: "" };
		};

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

		const editState: ButtonState = getEditDisabledState();
		const deleteState: ButtonState = getDeleteDisabledState();

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

			return (): void => {
				resizeObserver.disconnect();
			};
		}, [isEditing, activeTab, effectiveData]);

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
							<div key={toKey(fieldKey)} className={columnClass}>
								{isViewField(field)
									? renderModalViewField(field as ModalViewField, effectiveData, getModalId())
									: renderFormField(
											field as ModalFormField,
											formData,
											handleChange,
											errors,
											currentUser
										)}
							</div>
						);
					})}
				</div>
			);
		};

		// ----------------------------------------------------- DELETE ----------------------------------------------------

		const deactivateEntityConfirm: (item: JamData) => Promise<boolean> = useDeactivateEntityConfirm(entityType);
		const deleteEntityConfirm: (item: JamData) => Promise<boolean> = useDeleteEntityConfirm(entityType);
		const activateEntity: (item: JamData) => Promise<boolean> = useActivateEntity(entityType);
		const deactivateEntity: (item: JamData) => Promise<boolean> = useDeactivateEntity(entityType);

		const handleDeleteClick = async (): Promise<void> => {
			// Either deactivate or delete based on mode, then close the modal
			const handler: (item: JamData) => Promise<boolean> =
				mode === "import" ? deactivateEntityConfirm : deleteEntityConfirm;
			handler(effectiveData).then((result: boolean): void => {
				if (result) {
					handleHideImmediate();
					onDelete?.();
				}
			});
		};

		const handleActivateClick = async (): Promise<void> => {
			// Either deactivate or activate based on current state, then close the modal
			setActiveLoading(true);
			const handler: (item: JamData) => Promise<boolean> = effectiveData.is_active
				? deactivateEntity
				: activateEntity;
			handler(effectiveData).then((result: boolean): void => {
				if (result) {
					handleHideImmediate();
				}
				setActiveLoading(false);
			});
		};

		const handleChange = (e: SyntheticEvent): void => {
			const { name, type, checked, value } = e.target;
			const nextValue = type === "checkbox" ? checked : value;

			setFormData((prev) => {
				const next = structuredClone(prev);
				set(next, name, nextValue); // name like "premium.is_active"
				return next;
			});

			if (errors[name]) setErrors((prev) => ({ ...prev, [name]: "" }));
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
					if (tabFields.some((field: ModalFormField) => get(newErrors, field.name))) {
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
        ${entityName.toLowerCase()} due to the following error: ${err.message}`;
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
					return `modal-import-${entityType}`;
				}
				return `modal-edit-${entityType}`;
			} else {
				return `modal-view-${entityType}`;
			}
		};

		const renderHeader = (): JSX.Element => {
			let icon: string, text: string;
			if (mode === "add") {
				icon = "bi bi-plus-circle";
				text = `Add New ${entityName}`;
			} else if (mode === "import") {
				icon = "bi bi-download";
				text = `Import ${entityName}`;
			} else if (mode === "edit" || isEditing) {
				icon = "bi bi-pencil";
				text = `Edit ${entityName}`;
			} else {
				icon = "bi bi-eye";
				text = `${entityName} Details`;
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
										disabled={deleteState.disabled}
										tooltip={deleteState.message}
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
					// This handles "edit" mode (when user clicks edit in view/detail mode)
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
										fullWidth={false}
										disabled={deleteState.disabled}
										tooltip={deleteState.message}
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
							</div>
						</Modal.Footer>
					);
				}
			} else {
				// This handles "view" mode
				return showDeactivate ? (
					<Modal.Footer>
						<div className="d-flex flex-column w-100 gap-2">
							<div className="modal-buttons-container">
								<ActionButton
									id={getModalId() + "-deactivate-button"}
									variant="danger"
									onClick={handleActivateClick}
									loading={activeLoading}
									defaultText={effectiveData?.is_active ? "Deactivate" : "Activate"}
									loadingText={effectiveData?.is_active ? "Deactivating..." : "Activating..."}
									fullWidth={false}
								/>
								{canEdit && (
									<ActionButton
										id={getModalId() + "-edit-button"}
										variant="primary"
										onClick={handleEdit}
										defaultText="Edit"
										fullWidth={false}
										disabled={editState.disabled}
										tooltip={editState.message}
										tooltipPlacement="top"
									/>
								)}
							</div>
							<div className="modal-buttons-container">
								<ActionButton
									id={getModalId() + "-cancel-button"}
									variant="secondary"
									onClick={handleHideImmediate}
									defaultText="Close"
									fullWidth={false}
								/>
							</div>
						</div>
					</Modal.Footer>
				) : (
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
									disabled={editState.disabled}
									tooltip={editState.message}
									tooltipPlacement="top"
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
					className="data-modal"
					show={internalShow}
					onHide={handleCloseWithConfirmation}
					size={getModalSize(size)}
					centered={true}
					backdrop={true}
					keyboard={true}
					id={getModalId()}
				>
					{isEditing ? <Form onSubmit={handleSubmit}>{modalContent}</Form> : modalContent}
				</Modal>
			</>
		);
	}
);

export default DataModal;

export interface JamDataModalProps {
	onSuccess?: (data: any) => void;
	onDelete?: () => void;
	size?: "sm" | "lg" | "xl";
	canEdit?: boolean;
}
