import { Form } from "react-bootstrap";
import React from "react";
import Select from "react-select";

export const renderInputField = (field, formData, handleChange, errors, handleSelectChange, customFieldComponents = {}) => {
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

export const renderInputFieldGroup = (group, formData, handleChange, errors, handleSelectChange, customFieldComponents = {}) => {
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
							{renderInputField(field, formData, handleChange, errors, handleSelectChange, customFieldComponents)}
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
