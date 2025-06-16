
import { getCurrentDateTime } from "../utils/TimeUtils";
import { Button, Form, InputGroup } from "react-bootstrap";
import { useState, React } from "react";
import Select from "react-select";
import makeAnimated from 'react-select/animated';

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
			<i className="bi bi-plus-circle" style={{ fontSize: '21px' }}></i>
		</div>
	);
};

export const renderInputField = (
	field,
	formData,
	handleChange,
	errors,
	handleSelectChange,
	customFieldComponents = {},
) => {
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
			// For multiselect, ensure we have a valid array and options exist
			if (Array.isArray(value) && field.options && field.options.length > 0) {
				selectedValue = value
					.map(id => field.options.find(opt =>
						// Handle different data types for IDs
						opt.value == id || opt.value === parseInt(id) || opt.value === String(id)
					))
					.filter(Boolean); // Remove undefined values
			} else {
				selectedValue = []; // Always return empty array for multiselect
			}
		} else {
			// For single select
			if (value !== null && value !== undefined && value !== "" && field.options) {
				selectedValue = field.options.find((option) =>
					option.value == value || option.value === parseInt(value) || option.value === String(value)
				) || null;
			}
		}

		// Determine which components to use
		const selectComponents = { ...animatedComponents };

		// If there's an add button, replace the dropdown indicator
		if (field.addButton) {
			selectComponents.DropdownIndicator = CustomDropdownIndicator;
		}

		const selectComponent = (
			<Select
				name={field.name}
				value={selectedValue}
				onChange={(selectedOptions, actionMeta) => {
					if (isMulti) {
						// Extract just the IDs for storage in multiselect
						const ids = Array.isArray(selectedOptions)
							? selectedOptions.map(option => option.value)
							: [];

						const syntheticEvent = {
							target: {
								name: field.name,
								value: ids // Store as simple array of IDs
							}
						};
						handleChange(syntheticEvent);
					} else {
						// Handle single select
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
				className={`react-select-container ${error ? 'is-invalid' : ''}`}
				classNamePrefix="react-select"
				components={selectComponents}
				onAddButtonClick={field.addButton?.onClick} // Pass the onClick handler
				menuIsOpen={field.forceMenuClosed ? false : undefined} // Allow external control
				// Add these props to help maintain selection
				hideSelectedOptions={false}
				controlShouldRenderValue={true}
			/>
		);

		return selectComponent;
	}

	// Handle datetime-local with current time default and "Set Current Time" button
	if (field.type === "datetime-local") {
		const currentDateTime = getCurrentDateTime();

		const setCurrentTime = (e) => {
			e.preventDefault();
			const newDateTime = getCurrentDateTime();
			// Create a synthetic event to update the form
			const syntheticEvent = {
				target: {
					name: field.name,
					value: newDateTime,
				},
			};
			handleChange(syntheticEvent);
		};

		return (
			<InputGroup>
				<Form.Control
					type="datetime-local"
					name={field.name}
					value={value || currentDateTime}
					onChange={handleChange}
					isInvalid={!!error}
					placeholder={field.placeholder || "Select date and time"}
				/>
				<Button variant="outline-secondary" onClick={setCurrentTime} title="Set current time">
					<i className="bi bi-clock"></i>
				</Button>
			</InputGroup>
		);
	}

	// Handle custom field types
	if (field.type === "drag-drop" && customFieldComponents["drag-drop"]) {
		const DragDropComponent = customFieldComponents["drag-drop"];
		return (
			<DragDropComponent
				fieldName={field.name}
				label={field.label}
				value={value}
				onChange={handleChange}
				error={error}
			/>
		);
	}

	return (
		<Form.Control
			type={field.type || "text"}
			name={field.name}
			value={value || ""}
			onChange={handleChange}
			placeholder={field.placeholder}
			isInvalid={!!errors[field.name]}
			step={field.step}
		/>
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
							{errors[field.name] && field.type !== "drag-drop" && (
								<div className="d-block">{errors[field.name]}</div>
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

	// Default: full-width fields
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
					{errors[field.name] && field.type !== "drag-drop" && (
						<div className="invalid-feedback d-block">{errors[field.name]}</div>
					)}
				</Form.Group>
			))}
		</div>
	);
};