import { getCurrentDateTime } from "../utils/TimeUtils";
import { Button, Form, InputGroup } from "react-bootstrap";
import React from "react";
import Select from "react-select";

export const renderInputField = (
	field,
	formData,
	handleChange,
	errors,
	handleSelectChange,
	customFieldComponents = {},
) => {
	const value = formData[field.name] || "";
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

	if (field.type === "select") {
		const selectedValue = field.options?.find((option) => option.value === value);

		return (
			<Select
				name={field.name}
				value={selectedValue || null}
				onChange={(selectedOption, actionMeta) => handleSelectChange(selectedOption, actionMeta)}
				options={field.options}
				placeholder={field.placeholder || `Select ${field.label}`}
				isSearchable={field.isSearchable}
				isClearable={field.isClearable}
				isDisabled={field.isDisabled}
				isMulti={field.isMulti}
				menuPortalTarget={document.body}
				className="react-select-container"
				classNamePrefix="react-select"
			/>
		);
	}

	if (field.type === "multiselect") {
		console.log(field.options);
		// Convert array of IDs to react-select format
		let selectedValues = [];
		if (value && Array.isArray(value)) {
			selectedValues = value
				.map(id => field.options?.find(opt => opt.value === id))
				.filter(Boolean); // Remove any undefined values
		}
		console.log(selectedValues);

		return (
			<Select
				name={field.name}
				value={selectedValues}
				onChange={(selectedOptions, _actionMeta) => {
					// Extract just the IDs for storage
					const ids = selectedOptions ? selectedOptions.map(option => option.value) : [];

					const syntheticEvent = {
						target: {
							name: field.name,
							value: ids // Store as simple array of IDs
						}
					};

					handleChange(syntheticEvent);
				}}
				options={field.options || []}
				closeMenuOnSelect={false}
				placeholder={field.placeholder || `Select ${field.label}`}
				isSearchable={field.isSearchable !== false}
				isClearable={field.isClearable !== false}
				isDisabled={field.isDisabled}
				isMulti={true}
				menuPortalTarget={document.body}
				className={`react-select-container ${error ? 'is-invalid' : ''}`}
				classNamePrefix="react-select"
			/>
		);
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
								<div className="invalid-feedback d-block">{errors[field.name]}</div>
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