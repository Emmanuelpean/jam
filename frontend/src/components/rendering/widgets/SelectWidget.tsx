import React, { JSX, useCallback, useRef, useState } from "react";
import Select, { ActionMeta, MultiValue, SingleValue } from "react-select";
import makeAnimated from "react-select/animated";
import { SyntheticEvent, WidgetProps } from "./WidgetRenders";
import { FloatingPreview } from "../../FloatingPreview/FloatingPreview";
import { CustomSelectOption } from "../form/CustomSelectOption";
import { ModalViewFields } from "../view/ModalFields";
import { GroupedSelectOption, SelectOption } from "../form/FormOptions";
import { toKey } from "../../../utils/StringUtils";

export interface SelectWidgetPreviewConfig {
	enabled: boolean;
	fields: ModalViewFields;
	getDataById: (id: number) => any;
}

const animatedComponents = makeAnimated();

// Type guard to check if options are grouped
const isGroupedOptions = (
	options: readonly (SelectOption | GroupedSelectOption)[]
): options is readonly GroupedSelectOption[] => {
	return options.length > 0 && "options" in options[0]!;
};

// Helper function to find option in both flat and grouped arrays
const findOption = (
	options: readonly (SelectOption | GroupedSelectOption)[] | undefined,
	targetValue: string
): SelectOption | undefined => {
	if (!options || options.length === 0) return undefined;

	if (isGroupedOptions(options)) {
		// Search within grouped options
		for (const group of options) {
			const found = group.options.find((opt) => opt.value === targetValue);
			if (found) return found;
		}
		return undefined;
	} else {
		// Search flat options - type is now narrowed to SelectOption[]
		return (options as readonly SelectOption[]).find((opt) => opt.value === targetValue);
	}
};

const CustomDropdownIndicator = (props: any): JSX.Element => {
	const [hover, setHover] = useState(false);
	const menuIsOpen = props.selectProps.menuIsOpen;
	const isActive = hover || menuIsOpen;
	const customProps = props.selectProps;

	return (
		<div
			className={`custom-dropdown-indicator ${isActive ? "active" : ""}`}
			onMouseDown={(e: React.MouseEvent) => {
				e.preventDefault();
				e.stopPropagation();
				if (customProps.addButtonModalRef) {
					if (customProps.transformParentData && customProps.parentData) {
						const defaultData = customProps.transformParentData(customProps.parentData);
						customProps.addButtonModalRef.current?.showAdd(defaultData, (newData: any) => {
							if (customProps.onAddSuccess) {
								customProps.onAddSuccess(newData);
							}
						});
					} else {
						customProps.addButtonModalRef.current?.showAdd({}, (newData: any) => {
							if (customProps.onAddSuccess) {
								customProps.onAddSuccess(newData);
							}
						});
					}
				}
			}}
			onClick={(e: React.MouseEvent) => {
				e.preventDefault();
				e.stopPropagation();
			}}
			onMouseEnter={() => setHover(true)}
			onMouseLeave={() => setHover(false)}
			tabIndex={-1}
			aria-label="Add new item"
			role="button"
			title="Add new item"
			id="add-button"
		>
			<i className="bi bi-plus-circle"></i>
		</div>
	);
};

export const SelectInput = ({
	field,
	value,
	handleChange,
	error,
	secondaryValue,
	previewConfig,
	data,
}: WidgetProps): JSX.Element => {
	const [previewData, setPreviewData] = useState<any>(null);
	const [previewPosition, setPreviewPosition] = useState({ top: 0, left: 0 });
	const [showPreview, setShowPreview] = useState(false);
	const lastPreviewIdRef = useRef<string | null>(null);
	const isMulti: boolean = field.type === "multiselect";
	let selectedValue: SelectOption | SelectOption[] | null = null;

	const handleAddSuccess = useCallback(
		(newData: any) => {
			// Auto-select the newly added item
			const newId = newData.id;

			if (isMulti) {
				// For multi-select, add to existing values
				const currentIds = Array.isArray(value) ? value : [];
				const syntheticEvent: SyntheticEvent = {
					target: {
						name: toKey(field.name),
						value: [...currentIds, newId],
					},
				};
				handleChange(syntheticEvent);
			} else {
				// For single select, replace value
				const syntheticEvent: SyntheticEvent = {
					target: {
						name: toKey(field.name),
						value: newId,
					},
				};
				handleChange(syntheticEvent);
			}
		},
		[field.name, handleChange, isMulti, value]
	);

	const handleHover = useCallback(
		(option: SelectOption, position: { top: number; left: number }) => {
			if (previewConfig) {
				// Only update preview if different option
				if (lastPreviewIdRef.current === option.value) return;
				lastPreviewIdRef.current = option.value;

				const selectedData = previewConfig.getDataById(Number(option.value));
				setPreviewData(selectedData);
				setPreviewPosition(position);
				setShowPreview(true);
			}
		},
		[previewConfig]
	);

	const handleHoverEnd = useCallback(() => {
		lastPreviewIdRef.current = null;
		setShowPreview(false);
		setPreviewData(null);
	}, []);

	// Close preview when menu closes
	const handleMenuClose = useCallback(() => {
		setShowPreview(false);
		setPreviewData(null);
	}, []);

	if (isMulti) {
		if (Array.isArray(value) && value.length > 0 && field.options && field.options.length > 0) {
			selectedValue = value
				.map((item: any) => {
					const id = typeof item === "object" && item !== null ? item.id : item;
					return findOption(field.options, id);
				})
				.filter(Boolean) as SelectOption[];
		} else {
			selectedValue = [];
		}
	} else {
		if (value !== null && value !== undefined && value !== "" && field.options) {
			selectedValue = findOption(field.options, value) || null;
		}
	}

	const selectComponents = { ...animatedComponents };

	if (field.addButton?.modalRef) {
		selectComponents.DropdownIndicator = CustomDropdownIndicator;
	} else {
		selectComponents.DropdownIndicator = undefined;
		selectComponents.IndicatorSeparator = undefined;
	}

	if (previewConfig?.enabled) {
		selectComponents.Option = (props: any) => (
			<CustomSelectOption {...props} onHover={handleHover} onHoverEnd={handleHoverEnd} />
		);
	}

	const selectElement = (
		<>
			<Select<SelectOption, boolean>
				name={toKey(field.name)}
				value={selectedValue}
				onChange={(
					selectedOptions: MultiValue<SelectOption> | SingleValue<SelectOption>,
					_actionMeta: ActionMeta<SelectOption>
				) => {
					if (isMulti) {
						const ids: string[] = Array.isArray(selectedOptions)
							? selectedOptions.map((option: SelectOption) => option.value)
							: [];

						const syntheticEvent: SyntheticEvent = {
							target: {
								name: toKey(field.name),
								value: ids,
							},
						};
						handleChange(syntheticEvent);
					} else {
						const syntheticEvent: SyntheticEvent = {
							target: {
								name: toKey(field.name),
								value: selectedOptions ? (selectedOptions as SelectOption).value : null,
							},
						};
						handleChange(syntheticEvent);
					}
				}}
				onMenuClose={handleMenuClose}
				id={toKey(field.name)}
				options={field.options || []}
				closeMenuOnSelect={!isMulti}
				placeholder={field.placeholder || `Select ${field.label}`}
				isSearchable={field.isSearchable !== false}
				isClearable={field.isClearable !== false}
				isMulti={isMulti}
				menuPortalTarget={document.body}
				className={`react-select-container ${field.required ? "required" : ""} ${error ? "error" : ""}`}
				classNamePrefix="react-select"
				components={selectComponents}
				isDisabled={field.isDisabled}
				// @ts-ignore
				addButtonModalRef={field.addButton?.modalRef}
				parentData={data}
				transformParentData={field.addButton?.transformParentData}
				onAddSuccess={handleAddSuccess}
			/>
			{previewConfig?.enabled && (
				<FloatingPreview
					data={previewData}
					fields={previewConfig.fields}
					position={previewPosition}
					show={showPreview}
				/>
			)}
		</>
	);

	if (secondaryValue && secondaryValue.trim() !== "") {
		return (
			<div className="select-widget-with-secondary">
				<div className="secondary-value">{secondaryValue}</div>
				<div className="arrow-indicator">→</div>
				<div className="select-wrapper">{selectElement}</div>
			</div>
		);
	}

	return selectElement;
};
