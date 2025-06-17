import { getCurrentDateTime } from "../utils/TimeUtils";
import { Button, Form, InputGroup } from "react-bootstrap";
import { React, useState } from "react";
import Select from "react-select";
import makeAnimated from "react-select/animated";
import FileUploader from "../utils/FileUtils";

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

export const renderInputField = (field, formData, handleChange, errors, handleSelectChange) => {
	const value = formData[field.name];
	const error = errors[field.name];

	if (typeof field.render === "function") {
		return field.render({
			value: value || "",
			onChange: handleChange,
			formData,
			errors,
			handleSelectChange,
		});
	}

	if (field.type === "textarea") {
		return (
			<>
				<Form.Control
					as="textarea"
					rows={field.rows || 3}
					name={field.name}
					value={value || ""}
					onChange={handleChange}
					placeholder={field.placeholder}
					isInvalid={!!errors[field.name]}
					className="optimized-textarea"
				/>
				{error && <div className="invalid-feedback">{error}</div>}
			</>
		);
	}

	if (field.type === "checkbox") {
		return (
			<Form.Check
				type="checkbox"
				name={field.name}
				checked={value || false}
				onChange={handleChange}
				label={field.checkboxLabel || field.label}
			/>
		);
	}

	// Unified handling for both select and multiselect
	if (field.type === "select" || field.type === "multiselect") {
		const isMulti = field.type === "multiselect";
		let selectedValue = null;

		if (isMulti) {
			if (Array.isArray(value) && field.options && field.options.length > 0) {
				selectedValue = value
					.map((id) =>
						field.options.find(
							(opt) => opt.value == id || opt.value === parseInt(id) || opt.value === String(id),
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
							option.value == value || option.value === parseInt(value) || option.value === String(value),
					) || null;
			}
		}

		const selectComponents = { ...animatedComponents };

		if (field.addButton) {
			selectComponents.DropdownIndicator = CustomDropdownIndicator;
		}

		return (
			<>
				<Select
					name={field.name}
					value={selectedValue}
					onChange={(selectedOptions, actionMeta) => {
						if (isMulti) {
							const ids = Array.isArray(selectedOptions)
								? selectedOptions.map((option) => option.value)
								: [];

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
					menuIsOpen={field.forceMenuClosed ? false : undefined}
					hideSelectedOptions={false}
					controlShouldRenderValue={true}
				/>
				{error && <div className="invalid-feedback d-block">{error}</div>}
			</>
		);
	}

	// Handle datetime-local
	if (field.type === "datetime-local") {
		const currentDateTime = getCurrentDateTime();

		const formatDateTimeForInput = (dateTimeValue) => {
			if (!dateTimeValue) return currentDateTime;

			try {
				const date = new Date(dateTimeValue);
				if (isNaN(date.getTime())) {
					return currentDateTime;
				}

				const year = date.getFullYear();
				const month = String(date.getMonth() + 1).padStart(2, "0");
				const day = String(date.getDate()).padStart(2, "0");
				const hours = String(date.getHours()).padStart(2, "0");
				const minutes = String(date.getMinutes()).padStart(2, "0");

				return `${year}-${month}-${day}T${hours}:${minutes}`;
			} catch (error) {
				console.error("Error formatting datetime:", error);
				return currentDateTime;
			}
		};

		const setCurrentTime = (e) => {
			e.preventDefault();
			const newDateTime = getCurrentDateTime();
			const syntheticEvent = {
				target: {
					name: field.name,
					value: newDateTime,
				},
			};
			handleChange(syntheticEvent);
		};

		const formattedValue = formatDateTimeForInput(value);

		return (
			<>
				<InputGroup className={error ? "is-invalid" : ""}>
					<Form.Control
						type="datetime-local"
						name={field.name}
						value={formattedValue}
						onChange={handleChange}
						isInvalid={!!error}
						placeholder={field.placeholder || "Select date and time"}
					/>
					<Button variant="outline-secondary" onClick={setCurrentTime} title="Set current time">
						<i className="bi bi-clock"></i>
					</Button>
				</InputGroup>
				{error && <div className="invalid-feedback d-block">{error}</div>}
			</>
		);
	}

	// Handle drag-drop field type with new FileUploader
	if (field.type === "drag-drop") {
		return (
			<FileUploader
				fieldName={field.name}
				label={field.label}
				value={value}
				onChange={handleChange}
				error={error}
			/>
		);
	}

	return (
		<>
			<Form.Control
				type={field.type || "text"}
				name={field.name}
				value={value || ""}
				onChange={handleChange}
				placeholder={field.placeholder}
				isInvalid={!!errors[field.name]}
				step={field.step}
			/>
			{error && <div className="invalid-feedback">{error}</div>}
		</>
	);
};

export const renderInputFieldGroup = (
	group,
	formData,
	handleChange,
	errors,
	handleSelectChange,
	customFieldComponents = {},
) => {
	if (group.type === "row") {
		return (
			<div key={group.id || Math.random()} className={`row ${group.className || ""}`}>
				{group.fields.map((field) => (
					<div key={field.name} className={field.columnClass || "col-md-6"}>
						<Form.Group className="mb-3">
							{field.type !== "drag-drop" && (
								<Form.Label>
									{field.label}
									{field.required && <span className="text-danger">*</span>}
								</Form.Label>
							)}
							{renderInputField(
								field,
								formData,
								handleChange,
								errors,
								handleSelectChange,
								customFieldComponents,
							)}
						</Form.Group>
					</div>
				))}
			</div>
		);
	}

	if (group.type === "custom") {
		return (
			<div key={group.id || Math.random()} className={group.className || ""}>
				{group.content}
			</div>
		);
	}

	return (
		<div key={group.id || Math.random()}>
			{group.fields.map((field) => (
				<Form.Group key={field.name} className="mb-3">
					{field.type !== "drag-drop" && (
						<Form.Label>
							{field.label}
							{field.required && <span className="text-danger">*</span>}
						</Form.Label>
					)}
					{renderInputField(field, formData, handleChange, errors, handleSelectChange, customFieldComponents)}
				</Form.Group>
			))}
		</div>
	);
};
