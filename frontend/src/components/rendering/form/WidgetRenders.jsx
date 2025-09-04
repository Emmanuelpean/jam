import { formatDateTime } from "../../../utils/TimeUtils.ts";
import { Button, Form, InputGroup, Spinner } from "react-bootstrap";
import { React, useMemo, useState } from "react";
import Select from "react-select";
import makeAnimated from "react-select/animated";
import { useDropzone } from "react-dropzone";
import useGenericAlert from "../../../hooks/useGenericAlert.ts";
import AlertModal from "../../modals/AlertModal.tsx";
import { parseSizeText, formatFileSize } from "../../../utils/FileUtils.ts";
import "./WidgetRender.css";

const animatedComponents = makeAnimated();

const displayError = (errorMessage) => {
	if (!errorMessage) return null;
	return errorMessage.split("\n").map((line, index) => <div key={index}>{line}</div>);
};

// ---------------------------------------------------- STAR RATING ----------------------------------------------------

const StarRating = ({ field, value, handleChange, error }) => {
	const [hoverRating, setHoverRating] = useState(0);
	const maxRating = field.maxRating || 5;
	const currentRating = parseInt(value) || 0;

	const handleStarClick = (rating) => {
		const syntheticEvent = {
			target: {
				name: field.name,
				value: rating === currentRating ? 0 : rating,
			},
		};
		handleChange(syntheticEvent);
	};

	const handleStarHover = (rating) => {
		setHoverRating(rating);
	};

	const handleMouseLeave = () => {
		setHoverRating(0);
	};

	const getStarClass = (starNumber) => {
		const rating = hoverRating || currentRating;
		if (starNumber <= rating) {
			return "bi-star-fill";
		}
		return "bi-star";
	};

	return (
		<>
			<div className="star-rating-container">
				<div className="star-rating-stars" onMouseLeave={handleMouseLeave}>
					{[...Array(maxRating)].map((_, index) => {
						const starNumber = index + 1;
						return (
							<i
								key={starNumber}
								className={`star-rating-star ${getStarClass(starNumber)}`}
								onMouseEnter={() => handleStarHover(starNumber)}
								onClick={() => handleStarClick(starNumber)}
							/>
						);
					})}
				</div>
			</div>
			{error && (
				<div className="invalid-feedback d-block" id={`${field.name}-error-message`}>
					{displayError(error)}
				</div>
			)}
		</>
	);
};

const renderStarRating = (field, value, handleChange, error) => {
	return <StarRating field={field} value={value} handleChange={handleChange} error={error} />;
};

// ---------------------------------------------------- SALARY INPUT ---------------------------------------------------

const renderSalaryInput = (field, value, handleChange, error) => {
	return (
		<>
			<InputGroup>
				<InputGroup.Text>£</InputGroup.Text>
				<Form.Control
					id={field.name}
					type="number"
					name={field.name}
					value={value || ""}
					onChange={handleChange}
					placeholder={field.placeholder}
					isInvalid={!!error}
					step={field.step}
					min="0"
					className={error ? "is-invalid" : ""}
				/>
				<InputGroup.Text>/Year</InputGroup.Text>
			</InputGroup>
			{error && (
				<div className="invalid-feedback d-block" id={`${field.name}-error-message`}>
					{displayError(error)}
				</div>
			)}
		</>
	);
};

// --------------------------------------------------- ACTION BUTTON ---------------------------------------------------

export const ActionButton = ({
	id,
	variant = "primary",
	type = "button",
	size = "lg",
	className = "",
	disabled = false,
	loading = false,
	loadingText,
	defaultText,
	loadingIcon,
	defaultIcon,
	fullWidth = true,
	onClick,
	customContent,
	customLoadingContent,
	...otherProps
}) => {
	const buttonClasses = `${className} ${fullWidth ? "w-100" : ""}`.trim();

	const renderContent = () => {
		if (loading) {
			// Use custom loading content if provided
			if (customLoadingContent) {
				return customLoadingContent;
			}

			// Default loading content
			return (
				<>
					{loadingIcon ? (
						<i className={`${loadingIcon} me-2`}></i>
					) : (
						<Spinner
							as="span"
							animation="border"
							size="sm"
							role="status"
							aria-hidden="true"
							className="me-2"
						/>
					)}
					{loadingText}
				</>
			);
		}

		// Use custom content if provided
		if (customContent) {
			return customContent;
		}

		// Default content
		return (
			<>
				{defaultIcon && <i className={`${defaultIcon} me-2`}></i>}
				{defaultText}
			</>
		);
	};

	return (
		<Button
			id={id}
			variant={variant}
			type={type}
			size={size}
			disabled={disabled || loading}
			className={buttonClasses}
			onClick={onClick}
			{...otherProps}
		>
			{renderContent()}
		</Button>
	);
};

// ------------------------------------------------------- SELECT ------------------------------------------------------

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

const renderSelect = (field, value, handleChange, handleSelectChange, error) => {
	const isMulti = field.type === "multiselect";
	let selectedValue = null;

	if (isMulti) {
		if (Array.isArray(value) && value.length > 0 && field.options && field.options.length > 0) {
			selectedValue = value
				.map((item) => {
					// Extract the ID from the item (handle both objects with id property and primitive values)
					const id = typeof item === "object" && item !== null ? item.id : item;

					return field.options.find((opt) => opt.value === id);
				})
				.filter(Boolean);
		} else {
			selectedValue = [];
		}
	} else {
		if (value !== null && value !== undefined && value !== "" && field.options) {
			selectedValue = field.options.find((option) => option.value === value) || null;
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
				onChange={(selectedOptions, _actionMeta) => {
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
						const syntheticEvent = {
							target: {
								name: field.name,
								value: selectedOptions ? selectedOptions.value : null,
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
			{error && (
				<div className="invalid-feedback d-block" id={`${field.name}-error-message`}>
					{displayError(error)}
				</div>
			)}
		</>
	);
};

// --------------------------------------------------- PASSWORD INPUT --------------------------------------------------

const PasswordInput = ({ field, value, handleChange, error }) => {
	const [showPassword, setShowPassword] = useState(false);

	return (
		<>
			<div className="position-relative">
				<Form.Control
					type={showPassword ? "text" : "password"}
					id={field.name}
					name={field.name}
					placeholder={field.placeholder || "Enter your password"}
					value={value || ""}
					onChange={handleChange}
					size={field.size || "lg"}
					isInvalid={!!error}
					autoComplete={field.autoComplete || "current-password"}
					style={{ paddingRight: "50px" }}
				/>
				<button
					type="button"
					className={`password-toggle-btn ${showPassword ? "" : "show-slash"}`}
					onClick={() => setShowPassword(!showPassword)}
					tabIndex={field.tabIndex || 0}
				>
					<i className="bi bi-eye"></i>
				</button>
			</div>
			{error && (
				<div className="invalid-feedback d-block" id={`${field.name}-error-message`}>
					{displayError(error)}
				</div>
			)}
			{field.helpText && !error && <Form.Text className="text-muted">{field.helpText}</Form.Text>}
		</>
	);
};

const renderPasswordInput = (field, value, handleChange, error) => {
	return <PasswordInput field={field} value={value} handleChange={handleChange} error={error} />;
};

// ----------------------------------------------------- TEXT AREA -----------------------------------------------------

const renderTextarea = (field, value, handleChange, error) => {
	return (
		<>
			<Form.Control
				as="textarea"
				id={field.name}
				rows={field.rows || 3}
				name={field.name}
				value={value || ""}
				onChange={handleChange}
				placeholder={field.placeholder}
				isInvalid={!!error}
				className="optimized-textarea"
			/>
			{error && (
				<div className="invalid-feedback" id={`${field.name}-error-message`}>
					{displayError(error)}
				</div>
			)}
		</>
	);
};

// ------------------------------------------------------ CHECKBOX -----------------------------------------------------

const renderCheckbox = (field, value, handleChange) => {
	return (
		<Form.Check
			type="checkbox"
			id={field.name}
			name={field.name}
			checked={value || false}
			onChange={handleChange}
			label={field.checkboxLabel || field.label}
		/>
	);
};

// ------------------------------------------------------ DATETIME -----------------------------------------------------

const renderDateTimeLocal = (field, value, handleChange, error) => {
	const setCurrentTime = (e) => {
		e.preventDefault();
		e.stopPropagation();
		const newDateTime = formatDateTime();
		const syntheticEvent = {
			target: {
				name: field.name,
				value: newDateTime,
			},
		};
		handleChange(syntheticEvent);
	};

	// Use formatDateTime for formatting, defaults to current time if value is null/undefined
	const formattedValue = formatDateTime(value);

	return (
		<>
			<div className="datetime-input-wrapper">
				<Form.Control
					id={field.name}
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
			{error && (
				<div className="invalid-feedback d-block" id={`${field.name}-error-message`}>
					{displayError(error)}
				</div>
			)}
		</>
	);
};

// ---------------------------------------------------- DRAG & DROP ----------------------------------------------------

const renderDragDrop = (field) => {
	return (
		<FileUploader
			id={field.name}
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

const FileUploader = ({
	name,
	label,
	value,
	onChange,
	onRemove,
	onOpenFile,
	acceptedFileTypes = ".TXT, .PDF, .DOC, .DOCX",
	maxSizeText = "5 MB",
	required = false,
}) => {
	const { alertState, showError, hideAlert } = useGenericAlert();
	const maxSizeBytes = useMemo(() => parseSizeText(maxSizeText), [maxSizeText]);

	// Convert acceptedFileTypes to proper MIME types for react-dropzone
	const acceptTypes = useMemo(() => {
		const extensions = acceptedFileTypes.split(",").map((ext) => ext.trim().toLowerCase());
		const mimeTypes = {};

		extensions.forEach((ext) => {
			switch (ext) {
				case ".pdf":
					mimeTypes["application/pdf"] = [".pdf"];
					break;
				case ".doc":
					mimeTypes["application/msword"] = [".doc"];
					break;
				case ".docx":
					mimeTypes["application/vnd.openxmlformats-officedocument.wordprocessingml.document"] = [".docx"];
					break;
				case ".txt":
					mimeTypes["text/plain"] = [".txt"];
					break;
				case ".jpg":
				case ".jpeg":
					mimeTypes["image/jpeg"] = [".jpg", ".jpeg"];
					break;
				case ".png":
					mimeTypes["image/png"] = [".png"];
					break;
				default:
					mimeTypes[`*/*`] = extensions; // Fallback
			}
		});

		return mimeTypes;
	}, [acceptedFileTypes]);

	const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
		accept: acceptTypes,
		maxSize: maxSizeBytes,
		multiple: false,
		onDrop: (acceptedFiles) => {
			if (acceptedFiles.length > 0 && onChange) {
				onChange(acceptedFiles[0]);
			}
		},
		onDropRejected: (rejections) => {
			// Handle errors with custom error modal
			if (rejections.length > 0) {
				const rejection = rejections[0];
				const file = rejection.file;
				const errors = rejection.errors;

				// Find the most relevant error
				const sizeError = errors.find((err) => err.code === "file-too-large");
				const typeError = errors.find((err) => err.code === "file-invalid-type");

				if (sizeError) {
					showError({
						title: "File Upload Error",
						message: `File size must be less than ${maxSizeText}. Current file is ${formatFileSize(file.size)}.`,
						size: "md",
					});
				} else if (typeError) {
					showError({
						title: "File Upload Error",
						message: `Please upload a file with one of these extensions: ${acceptedFileTypes}`,
						size: "md",
					});
				} else {
					showError({
						title: "File Upload Error",
						message: errors[0]?.message || "File upload failed",
						size: "md",
					});
				}
			}
		},
	});

	const hasFile = value && (value instanceof File || (typeof value === "object" && value.filename));
	const fileName = value?.name || value?.filename || "";
	const fileSize = value?.size ? formatFileSize(value.size) : "";

	const handleRemove = (e) => {
		e.stopPropagation();
		if (onRemove) {
			onRemove();
		}
	};

	const handleDownload = (e) => {
		e.stopPropagation();
		if (value instanceof File) {
			const url = URL.createObjectURL(value);
			const link = document.createElement("a");
			link.href = url;
			link.download = value.name;
			link.click();
			URL.revokeObjectURL(url);
		} else if (onOpenFile && value) {
			try {
				onOpenFile(value);
			} catch (error) {
				console.error("Error downloading file:", error);
				showError({
					title: "Download Error",
					message: "Error downloading file. Please try again.",
					size: "md",
				});
			}
		}
	};

	return (
		<>
			<div className="file-uploader-container">
				{label && (
					<label className="form-label">
						{label}
						{required && <span className="text-danger ms-1">*</span>}
					</label>
				)}

				<div
					{...getRootProps()}
					className={`file-dropzone ${isDragActive ? "drag-active" : ""} ${isDragReject ? "drag-reject" : ""} ${hasFile ? "has-file" : ""}`}
				>
					<input {...getInputProps({ name })} />

					{isDragActive ? (
						<div className="dropzone-content">
							<i className="bi bi-cloud-arrow-down dropzone-icon text-primary"></i>
							<div className="dropzone-text">
								{isDragReject ? "File type not supported" : "Drop your file here"}
							</div>
						</div>
					) : hasFile ? (
						<div className="file-card">
							<div className="file-info">
								<i className="bi bi-file-earmark-text file-icon"></i>
								<div className="file-details">
									<div className="file-name">{fileName}</div>
									{fileSize && <small className="file-size text-muted">{fileSize}</small>}
								</div>
							</div>
							<div className="file-actions">
								<button
									type="button"
									className="btn-file-action btn-file-download"
									onClick={handleDownload}
									title="Download file"
								>
									<i className="bi bi-download"></i>
								</button>
								<button
									type="button"
									className="btn-file-action btn-file-remove"
									onClick={handleRemove}
									title="Remove file"
								>
									<i className="bi bi-trash"></i>
								</button>
							</div>
						</div>
					) : (
						<div className="dropzone-content">
							<i className="bi bi-cloud-arrow-up dropzone-icon"></i>
							<div className="dropzone-text">Drag & drop your file here</div>
							<div className="dropzone-text">Or click to select a file</div>
							<div className="dropzone-info">
								Max size: {maxSizeText} • {acceptedFileTypes.replace(/\./g, "").toUpperCase()}
							</div>
						</div>
					)}
				</div>
			</div>

			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</>
	);
};

// ------------------------------------------------------- TABLE -------------------------------------------------------

const renderTable = (field) => {
	if (field.render && typeof field.render === "function") {
		return field.render();
	}
	return <div>Table component not provided</div>;
};

// --------------------------------------------------- DEFAULT INPUT ---------------------------------------------------

export const renderDefaultInput = (field, value, handleChange, error) => {
	return (
		<>
			<Form.Control
				id={field.name}
				type={field.type || "text"}
				name={field.name}
				value={value || ""}
				onChange={handleChange}
				placeholder={field.placeholder}
				isInvalid={!!error}
				step={field.step}
				autoComplete={field.autoComplete}
			/>
			{error && (
				<div className="invalid-feedback" id={`${field.name}-error-message`}>
					{displayError(error)}
				</div>
			)}
		</>
	);
};

export const renderInputField = (field, formData, handleChange, errors, handleSelectChange) => {
	const value = field.type === "drag-drop" || field.type === "table" ? field.value : formData[field.name];
	const error = errors[field.name];

	// Handle custom render function
	if (typeof field.render === "function" && field.type !== "table") {
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

		case "password":
			return renderPasswordInput(field, value, handleChange, error);

		case "drag-drop":
			return renderDragDrop(field);

		case "table":
			return renderTable(field);

		case "salary":
			return renderSalaryInput(field, value, handleChange, error);

		case "rating":
			return renderStarRating(field, value, handleChange, error);

		default:
			return renderDefaultInput(field, value, handleChange, error);
	}
};
