
import { getCurrentDateTime } from "../utils/TimeUtils";
import { Button, Form, InputGroup } from "react-bootstrap";
import { useState, React, useCallback } from "react";
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

// Drag and Drop File Component
const DragDropFile = ({ fieldName, label, value, onChange, error, dragStates, setDragStates, validateFile, handleOpenFile, handleRemoveFile }) => {
	const handleDragEnter = useCallback(
		(e) => {
			e.preventDefault();
			setDragStates((prev) => ({ ...prev, [fieldName]: true }));
		},
		[fieldName, setDragStates],
	);

	const handleDragLeave = useCallback(
		(e) => {
			e.preventDefault();
			if (!e.currentTarget.contains(e.relatedTarget)) {
				setDragStates((prev) => ({ ...prev, [fieldName]: false }));
			}
		},
		[fieldName, setDragStates],
	);

	const handleDragOver = useCallback((e) => {
		e.preventDefault();
	}, []);

	const handleDrop = useCallback(
		async (e) => {
			e.preventDefault();
			setDragStates((prev) => ({ ...prev, [fieldName]: false }));

			const files = Array.from(e.dataTransfer.files);
			if (files.length > 0) {
				const file = files[0];
				const validation = validateFile(file);
				if (validation.valid) {
					const syntheticEvent = {
						target: {
							name: fieldName,
							value: file,
							files: [file]
						}
					};
					onChange(syntheticEvent);
				} else {
					console.error(validation.error);
					alert(validation.error);
				}
			}
		},
		[fieldName, onChange, setDragStates, validateFile],
	);

	const handleFileSelect = useCallback(
		async (e) => {
			const file = e.target.files[0];
			if (file) {
				const validation = validateFile(file);
				if (validation.valid) {
					const syntheticEvent = {
						target: {
							name: fieldName,
							value: file,
							files: e.target.files
						}
					};
					onChange(syntheticEvent);
				} else {
					e.target.value = "";
					console.error(validation.error);
					alert(validation.error);
				}
			}
		},
		[onChange, validateFile, fieldName],
	);

	const isDragging = dragStates[fieldName];
	const hasNewFile = value && value instanceof File;
	const hasExistingFile = value && typeof value === 'object' && value.filename && !value.name;
	const hasFile = hasNewFile || hasExistingFile;

	return (
		<div>
			<Form.Label>{label}</Form.Label>
			<div
				className={`drag-drop-zone ${isDragging ? "dragging" : ""} ${hasFile ? "has-file" : ""} ${error ? "is-invalid" : ""}`}
				onDragEnter={handleDragEnter}
				onDragLeave={handleDragLeave}
				onDragOver={handleDragOver}
				onDrop={handleDrop}
				style={{
					border: `2px dashed ${error ? "#dc3545" : isDragging ? "#0d6efd" : "#dee2e6"}`,
					borderRadius: "0.375rem",
					padding: "2rem 1rem",
					textAlign: "center",
					backgroundColor: isDragging ? "#f8f9fa" : hasFile ? "#e8f5e8" : "#fafafa",
					cursor: "pointer",
					transition: "all 0.2s ease",
					minHeight: "120px",
					display: "flex",
					flexDirection: "column",
					justifyContent: "center",
					alignItems: "center",
					position: "relative",
				}}
				onClick={() => document.getElementById(`${fieldName}-input`).click()}
			>
				<input
					id={`${fieldName}-input`}
					type="file"
					name={fieldName}
					accept=".pdf,.doc,.docx"
					onChange={handleFileSelect}
					style={{ display: "none" }}
				/>

				{hasFile && (
					<Button
						variant="outline-danger"
						size="sm"
						className="position-absolute"
						style={{ top: "8px", right: "8px", zIndex: 1 }}
						onClick={(e) => {
							e.stopPropagation();
							handleRemoveFile(fieldName, onChange);
						}}
						title="Remove file"
					>
						<i className="bi bi-x"></i>
					</Button>
				)}

				{hasNewFile ? (
					<>
						<i className="bi bi-check-circle-fill text-success mb-2" style={{ fontSize: "2rem" }}></i>
						<div className="fw-semibold text-success">{value.name}</div>
						<small className="text-muted">{(value.size / 1024 / 1024).toFixed(2)} MB</small>
						<small className="text-muted mt-1">Click to replace</small>
					</>
				) : hasExistingFile ? (
					<>
						<i className="bi bi-file-earmark-text text-info mb-2" style={{ fontSize: "2rem" }}></i>
						<div className="fw-semibold text-info mb-2">{value.filename}</div>
						<Button
							variant="outline-info"
							size="sm"
							className="mb-2"
							onClick={(e) => {
								e.stopPropagation();
								handleOpenFile(value);
							}}
						>
							<i className="bi bi-download me-1"></i>
							Open File
						</Button>
						<small className="text-muted">Click anywhere to replace</small>
					</>
				) : isDragging ? (
					<>
						<i className="bi bi-cloud-arrow-down text-primary mb-2" style={{ fontSize: "2rem" }}></i>
						<div className="fw-semibold text-primary">Drop your file here</div>
					</>
				) : (
					<>
						<i className="bi bi-cloud-arrow-up text-muted mb-2" style={{ fontSize: "2rem" }}></i>
						<div className="fw-semibold text-muted mb-1">
							Drag & drop your {label.toLowerCase()} here
						</div>
						<div className="text-muted mb-2">or</div>
						<Button variant="outline-primary" size="sm">
							<i className="bi bi-folder2-open me-1"></i>
							Browse Files
						</Button>
						<small className="text-muted mt-2">PDF, DOC, DOCX up to 10MB</small>
					</>
				)}
			</div>
			{error && <div className="invalid-feedback d-block mt-1">{error}</div>}
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
			if (Array.isArray(value) && field.options && field.options.length > 0) {
				selectedValue = value
					.map(id => field.options.find(opt =>
						opt.value == id || opt.value === parseInt(id) || opt.value === String(id)
					))
					.filter(Boolean);
			} else {
				selectedValue = [];
			}
		} else {
			if (value !== null && value !== undefined && value !== "" && field.options) {
				selectedValue = field.options.find((option) =>
					option.value == value || option.value === parseInt(value) || option.value === String(value)
				) || null;
			}
		}

		const selectComponents = { ...animatedComponents };

		if (field.addButton) {
			selectComponents.DropdownIndicator = CustomDropdownIndicator;
		}

		const selectComponent = (
			<Select
				name={field.name}
				value={selectedValue}
				onChange={(selectedOptions, actionMeta) => {
					if (isMulti) {
						const ids = Array.isArray(selectedOptions)
							? selectedOptions.map(option => option.value)
							: [];

						const syntheticEvent = {
							target: {
								name: field.name,
								value: ids
							}
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
				className={`react-select-container ${error ? 'is-invalid' : ''}`}
				classNamePrefix="react-select"
				components={selectComponents}
				onAddButtonClick={field.addButton?.onClick}
				menuIsOpen={field.forceMenuClosed ? false : undefined}
				hideSelectedOptions={false}
				controlShouldRenderValue={true}
			/>
		);

		return selectComponent;
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
				const month = String(date.getMonth() + 1).padStart(2, '0');
				const day = String(date.getDate()).padStart(2, '0');
				const hours = String(date.getHours()).padStart(2, '0');
				const minutes = String(date.getMinutes()).padStart(2, '0');

				return `${year}-${month}-${day}T${hours}:${minutes}`;
			} catch (error) {
				console.error('Error formatting datetime:', error);
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
			<InputGroup>
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
		);
	}

	// Handle drag-drop field type
	if (field.type === "drag-drop") {
		// Check if we have the required functions passed through customFieldComponents
		if (customFieldComponents["drag-drop"]) {
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

		// If no custom component provided, show a fallback message
		return (
			<div className="alert alert-warning">
				Drag and drop component not configured properly. Please provide drag-drop functions.
			</div>
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

// Export the DragDropFile component for use in other components
export { DragDropFile };

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