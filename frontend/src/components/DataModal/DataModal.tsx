import React, { forwardRef, JSX, ReactNode, useEffect, useImperativeHandle, useRef, useState } from "react";
import { Alert, Card, Form, Modal } from "react-bootstrap";
import JamModal from "../JamModal/JamModal";
import { ModalHeader } from "../ModalHeader/ModalHeader";
import LoadingSpinner from "../Spinner/Spinner";
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
import { areDifferent, findItemByKey, getColumnClass, normaliseArray } from "../../utils/Utils";
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
import { ModalSection } from "./ModalSection";
import { IsViewNull, ViewField } from "../rendering/view/ViewRenders";

export type Field = ModalViewField | ModalFormField;

export type GenericFormData = Record<string, any>;

export interface SectionConfig {
	type: "section";
	key: string;
	title: string;
	icon?: string;
	fields: (Field | Field[])[];
	displayCondition?: (data: any) => boolean;
	defaultExpanded?: boolean;
}

export type FieldItem = Field | Field[] | SectionConfig;
export type Fields = FieldItem[];

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

export interface DataModalProps<T extends JamData = JamData> {
	mode?: modalModes; // modal mode
	fields?: { view: Fields; form: Fields } | ((data: any, mode: string) => { view: Fields; form: Fields }); // fields to display
	data?: T; // data to populate the fields (required for import mode)
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
	extraViewFooterButtons?: (activeTab: string | null, data: any) => React.ReactNode; // extra buttons in view mode footer
	canEdit?: boolean | ((formData: any) => string); // Controls edit button and edit mode access
	canDelete?: boolean | ((formData: any) => string); // Controls delete button and edit mode access
	showDeactivate?: boolean; // whether to show deactivate items in view mode
	formExtraContent?: ((formData: GenericFormData) => React.ReactNode) | React.ReactNode; // extra content rendered below form fields in add/edit mode
}

interface ButtonState {
	disabled: boolean;
	message: string;
}

export interface ValidationErrors {
	[key: string]: string;
}

export interface DataModalHandle<T extends JamData = JamData> {
	showView: (data: T) => void;
	showEdit: (data: T) => void;
	showAdd: (data: any) => void;
	showImport: (data: T) => void;
}

type ExpandedStates = Record<string, boolean>;

function DataModalComponent<T extends JamData>(
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
		formExtraContent,
		extraViewFooterButtons,
	}: DataModalProps<T>,
	ref: React.Ref<DataModalHandle<T>>
) {
	const hasTabs = tabs && tabs.length > 0;
	const [internalShow, setInternalShow] = useState(false);
	const [mode, setMode] = useState<modalModes>("view");
	const [effectiveData, setEffectiveData] = useState<any>(null);
	useImperativeHandle(ref, () => ({
		showView: async (data: T): Promise<void> => {
			setMode("view");
			resetExpandedStates();
			setInternalShow(true);
			if (transformInputData) {
				setInputDataLoading(true);
				const processedData = await transformInputData(data);
				setEffectiveData(processedData);
				setInputDataLoading(false);
			} else {
				setEffectiveData(data);
			}
		},
		showEdit: async (data: T): Promise<void> => {
			setMode("edit");
			resetExpandedStates();
			setInternalShow(true);
			if (transformInputData) {
				setInputDataLoading(true);
				const processedData = await transformInputData(data);
				setEffectiveData(processedData);
				setInputDataLoading(false);
			} else {
				setEffectiveData(data);
			}
		},
		showAdd: async (data: any, successCallback?: (newData: T) => void): Promise<void> => {
			setMode("add");
			setOnSuccessCallback(() => successCallback || null);
			resetExpandedStates();
			setInternalShow(true);
			if (transformInputData) {
				setInputDataLoading(true);
				const processedData = await transformInputData(data);
				setEffectiveData(processedData);
				setInputDataLoading(false);
			} else {
				setEffectiveData(data);
			}
		},
		showImport: async (data: T): Promise<void> => {
			setMode("import");
			resetExpandedStates();
			setInternalShow(true);
			if (transformInputData) {
				setInputDataLoading(true);
				const processedData = await transformInputData(data);
				setEffectiveData(processedData);
				setInputDataLoading(false);
			} else {
				setEffectiveData(data);
			}
		},
	}));

	const [onSuccessCallback, setOnSuccessCallback] = useState<((data: any) => void) | null>(null);
	const [formData, setFormData] = useState<GenericFormData>({});
	const [originalFormData, setOriginalFormData] = useState<GenericFormData>({});
	const [submitting, setSubmitting] = useState<boolean>(false);
	const [activeLoading, setActiveLoading] = useState<boolean>(false);
	const [inputDataLoading, setInputDataLoading] = useState<boolean>(false);
	const [errors, setErrors] = useState<Errors>({});
	const [isEditing, setIsEditing] = useState<boolean>(false);
	const { currentUser } = useAuth();
	const dataContext: DataContextValue = useDataContext();
	const [activeTab, setActiveTab] = useState<string | null>((): string | null => {
		if (hasTabs) {
			return defaultActiveTab || tabs[0]!.key;
		}
		return null;
	});
	const contentRef = useRef<HTMLDivElement>(null);
	const { showDelete } = useAlert();
	const entityName: string = entityTypeToGenericName(entityType);
	const [expandedSections, setExpandedSections] = useState<ExpandedStates>({});

	const handleSectionToggle = (sectionKey: string, isExpanded: boolean): void => {
		setExpandedSections(
			(prev: ExpandedStates): ExpandedStates => ({
				...prev,
				[sectionKey]: isExpanded,
			})
		);
	};

	const isSectionExpanded = (sectionKey: string): boolean => {
		// If we have an explicit state for this section (user toggled), use it
		if (sectionKey in expandedSections) {
			return expandedSections[sectionKey]!;
		}

		// Compute default based on mode
		if (!isEditing) {
			// In view mode, collapse sections without data
			const allFields: Fields = getAllSectionFields();
			const section: SectionConfig | undefined = allFields.find(
				(f: FieldItem): f is SectionConfig => isSectionConfig(f) && f.key === sectionKey
			);
			// Use explicit defaultExpanded if set, otherwise collapse sections without data
			if (section?.defaultExpanded !== undefined) return section.defaultExpanded;
			return section ? sectionHasData(section, effectiveData) : true;
		}

		// In edit mode, default to expanded
		return true;
	};

	// Check if a field has displayable data
	const fieldHasData = (field: Field, data: any): boolean => {
		if (!data) return false;
		return !IsViewNull(dataContext, "", field as ViewField, data, "check");
	};

	// Check if a section has any fields with data
	const sectionHasData = (section: SectionConfig, data: any): boolean => {
		for (const item of section.fields) {
			if (Array.isArray(item)) {
				for (const field of item) {
					if (fieldHasData(field, data)) return true;
				}
			} else {
				if (fieldHasData(item, data)) return true;
			}
		}
		return false;
	};

	// Get all fields from all tabs or current fields
	const getAllSectionFields = (): Fields => {
		if (hasTabs && tabs) {
			const allFields: Fields = [];
			for (const tab of tabs) {
				allFields.push(...tab.fields.view);
				allFields.push(...tab.fields.form);
			}
			return allFields;
		}
		const fieldsConfig = typeof fields === "function" ? fields(effectiveData, mode) : fields;
		return [...(fieldsConfig?.view || []), ...(fieldsConfig?.form || [])];
	};

	const resetExpandedStates = (): void => {
		setExpandedSections({});
	};

	// ------------------------------------------------ MODAL STATE INIT ------------------------------------------------

	const getCurrentTabConfig = (): TabConfig | null => {
		if (!hasTabs) return null;
		return findItemByKey(tabs, activeTab) || tabs[0]!;
	};

	const isViewField = (field: Field): field is ModalViewField => {
		return !("name" in field) || "render" in field || "isTitle" in field;
	};

	const isSectionConfig = (item: FieldItem): item is SectionConfig => {
		return typeof item === "object" && !Array.isArray(item) && "type" in item && item.type === "section";
	};

	// Helper to get field name as string (handles string[] case)
	const getFieldName = (field: Field): string | null => {
		if (!("name" in field)) return null;
		return Array.isArray(field.name) ? (field.name[0] ?? null) : field.name;
	};

	// Flatten all fields including those inside sections for validation
	const flattenFieldsWithSections = (fieldItems: FieldItem[]): Field[] => {
		const result: Field[] = [];
		for (const item of fieldItems) {
			if (isSectionConfig(item)) {
				// Recursively flatten section fields
				result.push(...flattenFieldsWithSections(item.fields));
			} else if (Array.isArray(item)) {
				result.push(...item);
			} else {
				result.push(item);
			}
		}
		return result;
	};

	// Find section keys containing fields with errors
	const findSectionsWithErrors = (fieldItems: FieldItem[], errorFieldNames: string[]): string[] => {
		const sectionsWithErrors: string[] = [];

		const checkFieldsForErrors = (fields: (Field | Field[])[]): boolean => {
			for (const field of fields) {
				if (Array.isArray(field)) {
					for (const f of field) {
						const fieldName = getFieldName(f);
						if (fieldName && errorFieldNames.includes(fieldName)) {
							return true;
						}
					}
				} else {
					const fieldName = getFieldName(field);
					if (fieldName && errorFieldNames.includes(fieldName)) {
						return true;
					}
				}
			}
			return false;
		};

		for (const item of fieldItems) {
			if (isSectionConfig(item)) {
				if (checkFieldsForErrors(item.fields)) {
					sectionsWithErrors.push(item.key);
				}
			}
		}

		return sectionsWithErrors;
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

	// Run field-level liveValidation while the user types or when data loads into the form
	useEffect((): void => {
		if (!isEditing) return;

		const allFields: Field[] = flattenFieldsWithSections(getAllFields().form);
		const fieldsWithLive: ModalFormField[] = allFields.filter(
			(f: Field): f is ModalFormField => "liveValidation" in f && !!(f as ModalFormField).liveValidation
		);
		if (fieldsWithLive.length === 0) return;
		setErrors((prev: Errors): Errors => {
			const next = { ...prev };
			fieldsWithLive.forEach((field: ModalFormField): void => {
				const fieldName: string | null = getFieldName(field);
				if (!fieldName) return;
				const result: string | null = field.liveValidation!(formData[fieldName], formData, dataContext);
				if (result) {
					next[fieldName] = result;
				} else {
					delete next[fieldName];
				}
			});
			return next;
		});
	}, [formData, isEditing]);

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
		// Clear expanded sections to trigger recomputation based on view mode defaults
		setExpandedSections({});
	};

	const handleEdit = (): void => {
		setIsEditing(true);
		setFormData({ ...effectiveData });
		setOriginalFormData({ ...effectiveData });
		setExpandedSections({});
	};

	const editState: ButtonState = getEditDisabledState();
	const deleteState: ButtonState = getDeleteDisabledState();

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
				{itemList.map((field: Field, fieldIndex: number): JSX.Element => {
					const fieldKey: string | string[] =
						("key" in field ? field.key : null) ||
						("name" in field ? field.name : null) ||
						`field_${index}_${fieldIndex}`;

					return (
						<div key={toKey(fieldKey)} className={columnClass}>
							{isViewField(field)
								? renderModalViewField(field as ModalViewField, effectiveData, getModalId())
								: renderFormField(field as ModalFormField, formData, handleChange, errors, currentUser)}
						</div>
					);
				})}
			</div>
		);
	};

	const renderSection = (section: SectionConfig, index: number, isFormMode = true): JSX.Element => {
		return (
			<ModalSection
				key={section.key || index}
				sectionKey={section.key}
				title={section.title}
				icon={section.icon}
				expanded={isSectionExpanded(section.key)}
				onToggle={handleSectionToggle}
			>
				{section.fields.map(
					(item: Field | Field[], fieldIndex: number): JSX.Element =>
						renderFieldGroup(item, fieldIndex, isFormMode)
				)}
			</ModalSection>
		);
	};

	const renderFieldItem = (item: FieldItem, index: number, isFormMode = true): JSX.Element => {
		if (isSectionConfig(item)) {
			return renderSection(item, index, isFormMode);
		}
		return renderFieldGroup(item as Field | Field[], index, isFormMode);
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

	const filterConditionalFields = (fieldsToFilter: FieldItem[]): FieldItem[] => {
		return fieldsToFilter
			.map((item: FieldItem): FieldItem | null => {
				// Handle sections
				if (isSectionConfig(item)) {
					// Check section's own display condition
					if (item.displayCondition && !item.displayCondition(formData)) {
						return null;
					}
					// Filter fields within the section
					const filteredSectionFields = filterConditionalFields(item.fields) as (Field | Field[])[];
					if (filteredSectionFields.length === 0) {
						return null;
					}
					return { ...item, fields: filteredSectionFields };
				}

				// Handle arrays of fields
				if (Array.isArray(item)) {
					const filteredArray = item.filter((field: Field): boolean => {
						if (!field.displayCondition) {
							return true;
						} else {
							return field.displayCondition(formData);
						}
					});
					return filteredArray.length > 0 ? filteredArray : null;
				}

				// Handle single fields
				if (!item.displayCondition) {
					return item;
				} else {
					return item.displayCondition(formData) ? item : null;
				}
			})
			.filter((item: FieldItem | null): item is FieldItem => item !== null);
	};

	const validateFormFields = async (): Promise<Errors> => {
		const newErrors: Errors = {};
		const currentFields = getAllFields();
		const allFields = flattenFieldsWithSections(currentFields.form);

		// 1) Required field validation
		allFields.forEach((field: Field): void => {
			const fieldName: string | null = getFieldName(field);
			if ("required" in field && field.required && fieldName && !formData[fieldName]) {
				newErrors[fieldName] = `${field.label} is required`;
			}
		});

		// 2) Field custom validation
		for (const field of allFields) {
			const fieldName: string | null = getFieldName(field);
			if ("validation" in field && field.validation && fieldName) {
				const error: string | null = field.validation(formData[fieldName]);
				if (error) {
					newErrors[fieldName] = error;
				}
			}
		}

		// 2b) Field live validation
		for (const field of allFields) {
			const fieldName: string | null = getFieldName(field);
			if ("liveValidation" in field && (field as ModalFormField).liveValidation && fieldName) {
				const error: string | null = (field as ModalFormField).liveValidation!(
					formData[fieldName],
					formData,
					dataContext
				);
				if (error) {
					newErrors[fieldName] = error;
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

		// Switch to the tab containing the first error and expand sections with errors
		const errorFieldNames = Object.keys(newErrors);
		if (hasTabs && tabs) {
			for (const tab of tabs) {
				const tabFields: Field[] = flattenFieldsWithSections(filterConditionalFields(tab.fields.form));
				if (
					tabFields.some((field: Field): string | null => {
						const fieldName: string | null = getFieldName(field);
						return fieldName && get(newErrors, fieldName);
					})
				) {
					setActiveTab(tab.key);

					// Expand sections containing errors in this tab
					const sectionsToExpand = findSectionsWithErrors(
						filterConditionalFields(tab.fields.form),
						errorFieldNames
					);
					if (sectionsToExpand.length > 0) {
						setExpandedSections((prev: ExpandedStates): ExpandedStates => {
							const updated = { ...prev };
							sectionsToExpand.forEach((key: string): void => {
								updated[key] = true;
							});
							return updated;
						});
					}
					break;
				}
			}
		} else {
			// No tabs - expand sections with errors in current fields
			const currentFields = getCurrentFields();
			const sectionsToExpand = findSectionsWithErrors(currentFields.form, errorFieldNames);
			if (sectionsToExpand.length > 0) {
				setExpandedSections((prev: ExpandedStates): ExpandedStates => {
					const updated = { ...prev };
					sectionsToExpand.forEach((key: string): void => {
						updated[key] = true;
					});
					return updated;
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
			const validationErrors: Errors = await validateFormFields();
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
						onSuccess(mode === "import" ? formData : (apiResult.data as T));
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
			<ModalHeader onClose={handleCloseWithConfirmation}>
				<Modal.Title>
					<span style={{ display: "flex", alignItems: "center" }}>
						{icon && <i className={`${icon} me-2`} style={{ fontSize: "1.05em" }} />}
						<span>{text}</span>
					</span>
				</Modal.Title>
			</ModalHeader>
		);
	};

	const renderBodyContent = (): JSX.Element => {
		if (inputDataLoading) {
			return <LoadingSpinner text="Loading..." />;
		}

		const currentFields = getCurrentFields();
		const currentAdditionalFields: ModalViewField[] = getCurrentAdditionalFields();
		const warnings: WarningMessageConfig[] | null = warningMessage ? warningMessage(effectiveData) : null;

		const renderContentInner = (): JSX.Element => (
			<div className={`modal-content-visible`}>
				{warnings && warnings.length > 0 && (
					<>
						{warnings.map(
							({ key, message, variant }: WarningMessageConfig, idx: number): JSX.Element => (
								<Alert key={key ?? idx} variant={variant} className="mb-3">
									{message}
								</Alert>
							)
						)}
					</>
				)}
				{isEditing ? (
					<div>
						{errors.submit && <Alert variant="danger">{errors.submit}</Alert>}
						<div>
							{currentFields.form.map(
								(item: FieldItem, index: number): JSX.Element => (
									<div key={`form-field-${index}`}>{renderFieldItem(item, index, true)}</div>
								)
							)}
						</div>
						{formExtraContent &&
							(typeof formExtraContent === "function" ? formExtraContent(formData) : formExtraContent)}
					</div>
				) : (
					<div>
						{currentFields.view.length > 0 && (
							<Card>
								<Card.Body>
									<div>
										{currentFields.view.map(
											(item: FieldItem, index: number): JSX.Element => (
												<div key={`view-field-${index}`}>
													{renderFieldItem(item, index, false)}
												</div>
											)
										)}
									</div>
								</Card.Body>
							</Card>
						)}

						{currentAdditionalFields && currentAdditionalFields.length > 0 && (
							<div className="outside-card-content mt-3">
								{currentAdditionalFields.map(
									(item: ModalViewField, index: number): JSX.Element => (
										<div key={`outside-field-${index}`} className="mb-3">
											{renderModalViewField(item, effectiveData, getModalId())}
										</div>
									)
								)}
							</div>
						)}
					</div>
				)}
			</div>
		);

		return (
			<div className="modal-content-animated">
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
								{effectiveData?.is_active !== false && (
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
								)}
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
					{(() => {
						const extraButtons = extraViewFooterButtons?.(activeTab, effectiveData);
						return extraButtons ? (
							<div className="d-flex flex-column w-100 gap-2">
								<div className="modal-buttons-container">
									{extraButtons}
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
									/>
								</div>
							</div>
						) : (
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
						);
					})()}
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
			<JamModal
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
			</JamModal>
		</>
	);
}

const DataModal = forwardRef(DataModalComponent) as (<T extends JamData>(
	props: DataModalProps<T> & { ref?: React.Ref<DataModalHandle<T>> }
) => JSX.Element) & { displayName?: string };

export default DataModal;

export interface JamDataModalProps {
	onSuccess?: (data: any) => void;
	onDelete?: () => void;
	size?: "sm" | "lg" | "xl";
	canEdit?: boolean;
}
