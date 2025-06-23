import { formDateTime } from "../../utils/TimeUtils";
import { Form } from "react-bootstrap";
import { React, useState } from "react";
import Select from "react-select";
import makeAnimated from "react-select/animated";
import FileUploader from "../../utils/FileUtils";

const animatedComponents = makeAnimated();

const CustomDropdownIndicator = (props) => {
	const [hover, setHover] = useState(false);
	const menuIsOpen = props.selectProps.menuIsOpen;
	const isActive = hover || menuIsOpen;

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
			onMouseDown={(e) => {
				e.preventDefault();
				e.stopPropagation();
				if (props.selectProps.onAddButtonClick) {
					props.selectProps.onAddButtonClick(e);
				}
			}}
			onClick={(e) => {
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

const renderTextarea = (field, value, handleChange, error) => {
	return (
		<>
			<Form.Control
				as="textarea"
				rows={field.rows || 3}
				name={field.name}
				value={value || ""}
				onChange={handleChange}
				placeholder={field.placeholder}
				isInvalid={!!error}
				className="optimized-textarea"
			/>
			{error && <div className="invalid-feedback">{error}</div>}
		</>
	);
};

const renderCheckbox = (field, value, handleChange) => {
	return (
		<Form.Check
			type="checkbox"
			name={field.name}
			checked={value || false}
			onChange={handleChange}
			label={field.checkboxLabel || field.label}
		/>
	);
};

const renderSelect = (field, value, handleChange, handleSelectChange, error) => {
	const isMulti = field.type === "multiselect";
	let selectedValue = null;

	if (isMulti) {
		if (Array.isArray(value) && field.options && field.options.length > 0) {
			selectedValue = value
				.map((id) =>
					field.options.find(
						(opt) => opt.value === id || opt.value === parseInt(id) || opt.value === String(id),
					),
				)
				.filter(Boolean);
		} else {
			selectedValue = [];
		}
	} else {
		if (value !== null && value !== undefined && value !== "" && field.options) {
			selectedValue =
				field.options.find(
					(option) =>
						option.value === value || option.value === parseInt(value) || option.value === String(value),
				) || null;
		}
	}

	const selectComponents = { ...animatedComponents };

	if (field.addButton) {
		selectComponents.DropdownIndicator = CustomDropdownIndicator;
	} else {
		selectComponents.DropdownIndicator = null;
		selectComponents.IndicatorSeparator = null;
	}

	return (
		<>
			<Select
				name={field.name}
				value={selectedValue}
				onChange={(selectedOptions, actionMeta) => {
					if (isMulti) {
						const ids = Array.isArray(selectedOptions) ? selectedOptions.map((option) => option.value) : [];

						const syntheticEvent = {
							target: {
								name: field.name,
								value: ids,
							},
						};
						handleChange(syntheticEvent);
					} else {
						handleSelectChange(selectedOptions, actionMeta);
					}
				}}
				options={field.options || []}
				closeMenuOnSelect={!isMulti}
				placeholder={field.placeholder || `Select ${field.label}`}
				isSearchable={field.isSearchable !== false}
				isClearable={field.isClearable !== false}
				isDisabled={field.isDisabled}
				isMulti={isMulti}
				menuPortalTarget={document.body}
				className={`react-select-container ${error ? "is-invalid" : ""} ${field.required ? "required" : ""}`}
				classNamePrefix="react-select"
				components={selectComponents}
				onAddButtonClick={field.addButton?.onClick}
				hideSelectedOptions={false}
				controlShouldRenderValue={true}
			/>
			{error && <div className="invalid-feedback d-block">{error}</div>}
		</>
	);
};

// Render datetime-local widget
const renderDateTimeLocal = (field, value, handleChange, error) => {
	const setCurrentTime = (e) => {
		e.preventDefault();
		e.stopPropagation();
		const newDateTime = formDateTime(); // Gets current time formatted
		const syntheticEvent = {
			target: {
				name: field.name,
				value: newDateTime,
			},
		};
		handleChange(syntheticEvent);
	};

	// Use formDateTime for formatting, defaults to current time if value is null/undefined
	const formattedValue = formDateTime(value);

	return (
		<>
			<div className="datetime-input-wrapper">
				<Form.Control
					type="datetime-local"
					name={field.name}
					value={formattedValue}
					onChange={handleChange}
					isInvalid={!!error}
					placeholder={field.placeholder || "Select date and time"}
					className="datetime-input-with-icon"
				/>
				<i
					className="bi bi-clock datetime-embedded-icon"
					onClick={setCurrentTime}
					title="Set to current date and time"
				></i>
			</div>
			{error && <div className="invalid-feedback d-block">{error}</div>}
		</>
	);
};



// Render drag-drop widget
const renderDragDrop = (field) => {
	return (
		<FileUploader
			name={field.name}
			label={field.label}
			value={field.value}
			onChange={field.onChange}
			onRemove={field.onRemove}
			onOpenFile={field.onOpenFile}
			acceptedFileTypes={field.acceptedFileTypes}
			maxSizeText={field.maxSizeText}
			required={field.required}
		/>
	);
};

// Render default input widget
export const renderDefaultInput = (field, value, handleChange, error) => {
	return (
		<>
			<Form.Control
				type={field.type || "text"}
				name={field.name}
				value={value || ""}
				onChange={handleChange}
				placeholder={field.placeholder}
				isInvalid={!!error}
				step={field.step}
			/>
			{error && <div className="invalid-feedback">{error}</div>}
		</>
	);
};
export const renderInputField = (field, formData, handleChange, errors, handleSelectChange) => {
	// For drag-drop fields, don't use formData value since they manage their own state
	const value = field.type === "drag-drop" ? field.value : formData[field.name];
	const error = errors[field.name];

	// Handle custom render function
	if (typeof field.render === "function") {
		return field.render({
			value: value || "",
			onChange: handleChange,
			formData,
			errors,
			handleSelectChange,
		});
	}

	// Route to appropriate widget renderer based on field type
	switch (field.type) {
		case "textarea":
			return renderTextarea(field, value, handleChange, error);

		case "checkbox":
			return renderCheckbox(field, value, handleChange);

		case "select":
		case "multiselect":
			return renderSelect(field, value, handleChange, handleSelectChange, error);

		case "datetime-local":
			return renderDateTimeLocal(field, value, handleChange, error);

		case "drag-drop":
			return renderDragDrop(field);

		default:
			return renderDefaultInput(field, value, handleChange, error);
	}
};
