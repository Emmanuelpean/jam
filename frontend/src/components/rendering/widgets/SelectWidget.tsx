import React, { JSX, useCallback, useState } from "react";
import Select, { ActionMeta, GroupBase, MultiValue, SingleValue } from "react-select";
import makeAnimated from "react-select/animated";
import { SelectOption } from "../../../utils/Utils";
import { SyntheticEvent, WidgetProps } from "./WidgetRenders";
import "./SelectWidget.css";
import { FloatingPreview } from "../../FloatingPreview/FloatingPreview";
import { CustomSelectOption } from "../form/CustomSelectOption";
import { ModalViewFields } from "../view/ModalFields";

export interface SelectWidgetPreviewConfig {
	enabled: boolean;
	fields: ModalViewFields;
	getDataById: (id: string) => any;
}

const animatedComponents = makeAnimated();

const CustomDropdownIndicator = (props: any): JSX.Element => {
	const [hover, setHover] = useState<boolean>(false);
	const menuIsOpen = props.selectProps.menuIsOpen;
	const isActive = hover || menuIsOpen;
	const customProps = props.selectProps;

	return (
		<div
			style={{
				display: "flex",
				alignItems: "center",
				marginLeft: 11,
				boxSizing: "border-box",
				cursor: "pointer",
				color: isActive ? "hsl(0, 0%, 60%)" : "hsl(0, 0%, 80%)",
				transition: "color 150ms",
			}}
			onMouseDown={(e: React.MouseEvent) => {
				e.preventDefault();
				e.stopPropagation();
				if (customProps.onAddButtonClick) {
					customProps.onAddButtonClick(e);
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
			<i className="bi bi-plus-circle" style={{ fontSize: "21px" }}></i>
		</div>
	);
};

export const RenderSelect = ({
	field,
	value,
	handleChange,
	error,
	secondaryValue,
	previewConfig,
}: WidgetProps): JSX.Element => {
	const [previewData, setPreviewData] = useState<any>(null);
	const [previewPosition, setPreviewPosition] = useState({ top: 0, left: 0 });
	const [showPreview, setShowPreview] = useState(false);

	const handleHover = useCallback(
		(option: SelectOption, position: { top: number; left: number }) => {
			if (previewConfig) {
				const data = previewConfig.getDataById(option.value);
				setPreviewData(data);
				setPreviewPosition(position);
				setShowPreview(true);
			}
		},
		[previewConfig],
	);

	const handleHoverEnd = useCallback(() => {
		setShowPreview(false);
		setPreviewData(null);
	}, []);

	// Close preview when menu closes
	const handleMenuClose = useCallback(() => {
		setShowPreview(false);
		setPreviewData(null);
	}, []);

	const isMulti = field.type === "multiselect";
	let selectedValue: SelectOption | SelectOption[] | null = null;

	if (isMulti) {
		if (Array.isArray(value) && value.length > 0 && field.options && field.options.length > 0) {
			selectedValue = value
				.map((item: any) => {
					const id = typeof item === "object" && item !== null ? item.id : item;
					return field.options!.find((opt) => opt.value === id);
				})
				.filter(Boolean) as SelectOption[];
		} else {
			selectedValue = [];
		}
	} else {
		if (value !== null && value !== undefined && value !== "" && field.options) {
			selectedValue = field.options.find((option) => option.value === value) || null;
		}
	}

	const selectComponents = { ...animatedComponents };

	if (field.addButton?.onClick) {
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
			<Select<SelectOption, boolean, GroupBase<SelectOption>>
				name={field.name}
				value={selectedValue}
				onChange={(
					selectedOptions: MultiValue<SelectOption> | SingleValue<SelectOption>,
					_actionMeta: ActionMeta<SelectOption>,
				) => {
					if (isMulti) {
						const ids: string[] = Array.isArray(selectedOptions)
							? selectedOptions.map((option: SelectOption) => option.value)
							: [];

						const syntheticEvent: SyntheticEvent = {
							target: {
								name: field.name,
								value: ids,
							},
						};
						handleChange(syntheticEvent);
					} else {
						const syntheticEvent: SyntheticEvent = {
							target: {
								name: field.name,
								value: selectedOptions ? (selectedOptions as SelectOption).value : null,
							},
						};
						handleChange(syntheticEvent);
					}
				}}
				onMenuClose={handleMenuClose}
				id={field.name}
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
				hideSelectedOptions={false}
				controlShouldRenderValue={true}
				// @ts-ignore
				onAddButtonClick={field.addButton?.onClick}
				styles={{
					control: (base, state) => ({
						...base,
						borderColor: error ? "red" : state.isFocused ? "#2684FF" : base.borderColor,
						boxShadow: error ? "0 0 0 1px red" : state.isFocused ? "0 0 0 1px #2684FF" : base.boxShadow,
						"&:hover": {
							borderColor: error ? "red" : state.isFocused ? "#2684FF" : base.borderColor,
						},
					}),
				}}
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
			<div
				className="select-widget-with-secondary"
				style={{
					display: "flex",
					alignItems: "center",
					gap: "12px",
					width: "100%",
				}}
			>
				<div
					className="secondary-value"
					style={{
						padding: "8px 12px",
						backgroundColor: "#f5f5f5",
						border: "1px solid #ccc",
						borderRadius: "4px",
						fontSize: "14px",
						color: "#333",
						whiteSpace: "nowrap",
						minWidth: "fit-content",
					}}
				>
					{secondaryValue}
				</div>
				<div
					className="arrow-indicator"
					style={{
						fontSize: "18px",
						color: "#666",
						userSelect: "none",
						minWidth: "20px",
						textAlign: "center",
					}}
				>
					→
				</div>
				<div style={{ flex: 1, minWidth: 0 }}>{selectElement}</div>
			</div>
		);
	}

	return selectElement;
};
