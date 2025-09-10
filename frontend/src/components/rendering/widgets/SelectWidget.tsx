import React, { useState, JSX } from "react";
import Select from "react-select";
import makeAnimated from "react-select/animated";
import { ActionMeta, MultiValue, SingleValue } from "react-select";
import { SelectOption } from "../../../utils/Utils";
import { GroupBase } from "react-select";
import { SyntheticEvent, WidgetProps } from "./WidgetRenders";
import "./SelectWidget.css";
const animatedComponents = makeAnimated();

// Create a wrapper component that matches react-select's expected signature
const CustomDropdownIndicator = (props: any): JSX.Element => {
	const [hover, setHover] = useState<boolean>(false);
	const menuIsOpen = props.selectProps.menuIsOpen;
	const isActive = hover || menuIsOpen;

	// Type assertion to access custom props
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
		>
			<i className="bi bi-plus-circle" style={{ fontSize: "21px" }}></i>
		</div>
	);
};

export const renderSelect = ({ field, value, handleChange, error }: WidgetProps): JSX.Element => {
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

	return (
		<Select<SelectOption, boolean, GroupBase<SelectOption>>
			name={field.name}
			value={selectedValue}
			onChange={(
				selectedOptions: MultiValue<SelectOption> | SingleValue<SelectOption>,
				_actionMeta: ActionMeta<SelectOption>,
			) => {
				if (isMulti) {
					const ids = Array.isArray(selectedOptions)
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
			/** 👇 NEW: Add isInvalid support */
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
	);
};
