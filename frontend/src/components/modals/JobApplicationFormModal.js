import React, { useMemo, useRef, useState, useCallback } from "react";
import { Button, InputGroup, Form } from "react-bootstrap";
import GenericModal from "../GenericModal";

const JobApplicationFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false, jobId }) => {
    const dateInputRef = useRef(null);
    const [dragStates, setDragStates] = useState({ cv: false, cover_letter: false });

    // Generate current datetime in the format required for datetime-local input
    const getCurrentDateTime = () => {
        const now = new Date();
        // Format as YYYY-MM-DDTHH:MM for datetime-local input
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}`;
    };

    const currentDateTime = useMemo(() => getCurrentDateTime(), [show]);

    // Function to set current time
    const setCurrentTime = () => {
        const newDateTime = getCurrentDateTime();
        if (dateInputRef.current) {
            dateInputRef.current.value = newDateTime;
            // Trigger change event to update form state
            const event = new Event('input', { bubbles: true });
            dateInputRef.current.dispatchEvent(event);
        }
    };

    // Prepare initial data with defaults and clean values
    const preparedInitialData = useMemo(() => {
        const cleanedData = {
            status: "Applied", // Default status
            date: currentDateTime, // Set to current time when modal opens
            url: "", // Ensure string value
            note: "", // Ensure string value
            ...initialData, // Override with any provided initial data
        };

        // Clean up any null/undefined values that could cause form issues
        Object.keys(cleanedData).forEach(key => {
            if (cleanedData[key] === null || cleanedData[key] === undefined) {
                if (key === 'date') {
                    cleanedData[key] = currentDateTime;
                } else if (key === 'status') {
                    cleanedData[key] = "Applied";
                } else if (typeof cleanedData[key] === 'string' || key === 'url' || key === 'note') {
                    cleanedData[key] = "";
                } else {
                    delete cleanedData[key]; // Remove file fields and other non-string fields
                }
            }
        });

        // Specifically remove file fields from initial data to prevent form issues
        delete cleanedData.cv;
        delete cleanedData.cover_letter;

        return cleanedData;
    }, [initialData, currentDateTime]);

    // Validate file type and size
    const validateFile = (file) => {
        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        const maxSize = 10 * 1024 * 1024; // 10MB

        if (!allowedTypes.includes(file.type)) {
            return { valid: false, error: 'Please upload a PDF, DOC, or DOCX file' };
        }
        if (file.size > maxSize) {
            return { valid: false, error: 'File size must be less than 10MB' };
        }
        return { valid: true };
    };

    // Create drag and drop component
    const DragDropFile = ({ fieldName, label, value, onChange, error }) => {
        const handleDragEnter = useCallback((e) => {
            e.preventDefault();
            setDragStates(prev => ({ ...prev, [fieldName]: true }));
        }, [fieldName]);

        const handleDragLeave = useCallback((e) => {
            e.preventDefault();
            if (!e.currentTarget.contains(e.relatedTarget)) {
                setDragStates(prev => ({ ...prev, [fieldName]: false }));
            }
        }, [fieldName]);

        const handleDragOver = useCallback((e) => {
            e.preventDefault();
        }, []);

        const handleDrop = useCallback((e) => {
            e.preventDefault();
            setDragStates(prev => ({ ...prev, [fieldName]: false }));

            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) {
                const file = files[0];
                const validation = validateFile(file);
                if (validation.valid) {
                    onChange({ target: { name: fieldName, files: [file] } });
                } else {
                    // You might want to show this error somewhere
                    console.error(validation.error);
                }
            }
        }, [fieldName, onChange]);

        const handleFileSelect = useCallback((e) => {
            const file = e.target.files[0];
            if (file) {
                const validation = validateFile(file);
                if (validation.valid) {
                    onChange(e);
                } else {
                    // Clear the input and show error
                    e.target.value = '';
                    console.error(validation.error);
                }
            }
        }, [onChange]);

        const isDragging = dragStates[fieldName];
        const hasFile = value && value.name;

        return (
            <div>
                <Form.Label>
                    {label}
                </Form.Label>
                <div
                    className={`drag-drop-zone ${isDragging ? 'dragging' : ''} ${hasFile ? 'has-file' : ''} ${error ? 'is-invalid' : ''}`}
                    onDragEnter={handleDragEnter}
                    onDragLeave={handleDragLeave}
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                    style={{
                        border: `2px dashed ${error ? '#dc3545' : isDragging ? '#0d6efd' : '#dee2e6'}`,
                        borderRadius: '0.375rem',
                        padding: '2rem 1rem',
                        textAlign: 'center',
                        backgroundColor: isDragging ? '#f8f9fa' : hasFile ? '#e8f5e8' : '#fafafa',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        minHeight: '120px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        alignItems: 'center'
                    }}
                    onClick={() => document.getElementById(`${fieldName}-input`).click()}
                >
                    <input
                        id={`${fieldName}-input`}
                        type="file"
                        name={fieldName}
                        accept=".pdf,.doc,.docx"
                        onChange={handleFileSelect}
                        style={{ display: 'none' }}
                    />

                    {hasFile ? (
                        <>
                            <i className="bi bi-check-circle-fill text-success mb-2" style={{ fontSize: '2rem' }}></i>
                            <div className="fw-semibold text-success">{value.name}</div>
                            <small className="text-muted">{(value.size / 1024 / 1024).toFixed(2)} MB</small>
                            <small className="text-muted mt-1">Click to replace</small>
                        </>
                    ) : isDragging ? (
                        <>
                            <i className="bi bi-cloud-arrow-down text-primary mb-2" style={{ fontSize: '2rem' }}></i>
                            <div className="fw-semibold text-primary">Drop your file here</div>
                        </>
                    ) : (
                        <>
                            <i className="bi bi-cloud-arrow-up text-muted mb-2" style={{ fontSize: '2rem' }}></i>
                            <div className="fw-semibold text-muted mb-1">
                                Drag & drop your {label.toLowerCase()} here
                            </div>
                            <div className="text-muted mb-2">or</div>
                            <Button variant="outline-primary" size="sm">
                                <i className="bi bi-folder2-open me-1"></i>
                                Browse Files
                            </Button>
                            <small className="text-muted mt-2">
                                PDF, DOC, DOCX up to 10MB
                            </small>
                        </>
                    )}
                </div>
                {error && (
                    <div className="invalid-feedback d-block mt-1">
                        {error}
                    </div>
                )}
            </div>
        );
    };

    // Define layout groups for job application fields
    const layoutGroups = [
        // Job Application Fields Section
        {
            id: "application-header",
            type: "custom",
            className: "mb-3",
            content: (
                <div>
                    <h5 className="mb-0">
                        <i className="bi bi-file-earmark-text me-2"></i>
                        Application Details
                    </h5>
                    <small className="text-muted">Track your application progress and files</small>
                </div>
            ),
        },
        // Application Date and Status
        {
            id: "application-date-status",
            type: "row",
            fields: [
                {
                    name: "date",
                    label: "Application Date",
                    type: "custom",
                    required: true,
                    columnClass: "col-md-6",
                    render: (value, onChange, error) => (
                        <div>
                            <InputGroup>
                                <Form.Control
                                    ref={dateInputRef}
                                    type="datetime-local"
                                    value={value || currentDateTime}
                                    onChange={(e) => onChange(e.target.value)}
                                    isInvalid={!!error}
                                    placeholder="Select application date and time"
                                />
                                <Button
                                    variant="outline-secondary"
                                    onClick={setCurrentTime}
                                    title="Set to current time"
                                    size="sm"
                                    style={{
                                        border: "1.5px solid #dee2e6",
                                    }}
                                >
                                    <i className="bi bi-clock"></i>
                                </Button>
                            </InputGroup>
                            {error && (
                                <div className="invalid-feedback d-block">
                                    {error}
                                </div>
                            )}
                        </div>
                    ),
                },
                {
                    name: "status",
                    label: "Application Status",
                    type: "select",
                    options: [
                        { value: "Applied", label: "Applied" },
                        { value: "Interview", label: "Interview" },
                        { value: "Rejected", label: "Rejected" },
                        { value: "Offer", label: "Offer" },
                        { value: "Withdrawn", label: "Withdrawn" },
                    ],
                    required: true,
                    columnClass: "col-md-6",
                },
            ],
        },
        // Application URL
        {
            id: "application-url",
            type: "default",
            fields: [
                {
                    name: "url",
                    label: "Application URL",
                    type: "url",
                    placeholder: "https://... (link to your application submission)",
                },
            ],
        },
        // Application Note
        {
            id: "application-note",
            type: "default",
            fields: [
                {
                    name: "note",
                    label: "Application Notes",
                    type: "textarea",
                    rows: 3,
                    placeholder: "Add notes about your application process, interview details, etc...",
                },
            ],
        },
        // File Uploads Section
        {
            id: "files-header",
            type: "custom",
            className: "mt-4 mb-3",
            content: (
                <div className="border-top pt-3">
                    <h6 className="mb-0">
                        <i className="bi bi-paperclip me-2"></i>
                        Application Documents
                    </h6>
                    <small className="text-muted">Upload your CV and cover letter by dragging and dropping</small>
                </div>
            ),
        },
        // File uploads (side by side) - now using custom drag and drop
        {
            id: "application-files",
            type: "row",
            fields: [
                {
                    name: "cv",
                    label: "CV/Resume",
                    type: "drag-drop",
                    columnClass: "col-md-6",
                },
                {
                    name: "cover_letter",
                    label: "Cover Letter",
                    type: "drag-drop",
                    columnClass: "col-md-6",
                },
            ],
        },
    ];

    // Custom validation rules for application fields
    const validationRules = {
        date: (value) => {
            if (value) {
                const selectedDate = new Date(value);
                const now = new Date();
                if (selectedDate > now) {
                    return {
                        isValid: false,
                        message: "Application date cannot be in the future",
                    };
                }
            }
            return { isValid: true };
        },
        cv: (value) => {
            if (value && value.size > 10 * 1024 * 1024) { // 10MB limit
                return {
                    isValid: false,
                    message: "CV file size must be less than 10MB",
                };
            }
            return { isValid: true };
        },
        cover_letter: (value) => {
            if (value && value.size > 10 * 1024 * 1024) { // 10MB limit
                return {
                    isValid: false,
                    message: "Cover letter file size must be less than 10MB",
                };
            }
            return { isValid: true };
        },
    };

    // Transform form data before submission
    const transformFormData = (data) => {
        const transformed = { ...data };

        // Convert date to ISO string for backend
        if (transformed.date) {
            transformed.date = new Date(transformed.date).toISOString();
        }

        // Set default status if not provided
        if (!transformed.status) {
            transformed.status = "Applied";
        }

        // Add job_id if provided (for creating new applications)
        if (jobId) {
            transformed.job_id = jobId;
        }

        // Clean up empty string values - convert to null for backend
        if (transformed.url && !transformed.url.trim()) {
            delete transformed.url;
        }
        if (transformed.note && !transformed.note.trim()) {
            delete transformed.note;
        }

        // Handle file fields properly
        if (!transformed.cv || transformed.cv === "") {
            delete transformed.cv;
        }
        if (!transformed.cover_letter || transformed.cover_letter === "") {
            delete transformed.cover_letter;
        }

        return transformed;
    };

    return (
        <GenericModal
            show={show}
            onHide={onHide}
            mode="form"
            title={isEdit ? "Edit Job Application" : "New Job Application"}
            size={size}
            useCustomLayout={true}
            layoutGroups={layoutGroups}
            initialData={preparedInitialData}
            endpoint="jobapplications"
            onSuccess={onSuccess}
            validationRules={validationRules}
            transformFormData={transformFormData}
            isEdit={isEdit}
            customFieldComponents={{ "drag-drop": DragDropFile }}
        />
    );
};

export default JobApplicationFormModal;