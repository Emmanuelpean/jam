import React, { JSX, useCallback, useRef, useState } from "react";
import { SyntheticEvent, WidgetProps } from "./WidgetRenders";
import { FloatingPreview } from "../../FloatingPreview/FloatingPreview";
import { CustomSelect } from "./CustomSelect";
import { ModalViewFields } from "../view/ModalFields";
import { GroupedSelectOption, SelectOption } from "../form/FormOptions";
import { toKey } from "../../../utils/StringUtils";

export interface SelectWidgetPreviewConfig {
	enabled: boolean;
	fields: ModalViewFields;
	getDataById: (id: number) => any;
}

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
						name: toKey(field.key),
						value: [...currentIds, newId],
					},
				};
				handleChange(syntheticEvent);
			} else {
				// For single select, replace value
				const syntheticEvent: SyntheticEvent = {
					target: {
						name: toKey(field.key),
						value: newId,
					},
				};
				handleChange(syntheticEvent);
			}
		},
		[field.key, handleChange, isMulti, value]
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

	const selectElement = (
		<>
			<CustomSelect
				id={toKey(field.key)}
				name={toKey(field.key)}
				value={selectedValue}
				onChange={(selected) => {
					if (isMulti) {
						const ids: string[] = Array.isArray(selected)
							? (selected as SelectOption[]).map((option) => option.value)
							: [];
						handleChange({ target: { name: toKey(field.key), value: ids } });
					} else {
						handleChange({
							target: {
								name: toKey(field.key),
								value: selected ? (selected as SelectOption).value : null,
							},
						});
					}
				}}
				onMenuClose={handleMenuClose}
				options={field.options || []}
				closeMenuOnSelect={!isMulti}
				placeholder={field.placeholder || `Select ${field.label}`}
				isSearchable={field.isSearchable !== false}
				isClearable={field.isClearable !== false}
				isMulti={isMulti}
				className={`jam-select ${field.required ? "required" : ""} ${error ? "error" : ""}`}
				isDisabled={field.isDisabled}
				addButton={
					field.addButton?.modalRef
						? {
								modalRef: field.addButton.modalRef,
								transformParentData: field.addButton.transformParentData,
								onSuccess: handleAddSuccess,
								id: field.addButton.id,
						  }
						: undefined
				}
				parentData={data}
				previewHandlers={
					previewConfig?.enabled ? { onHover: handleHover, onHoverEnd: handleHoverEnd } : undefined
				}
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
