
import React, { useEffect, useState } from 'react';
import { Alert, Button, Form, Modal } from 'react-bootstrap';
import Select from 'react-select';
import { useAuth } from '../contexts/AuthContext';
import '../index.css';

const GenericFormModal = ({
                              show,
                              onHide,
                              title,
                              fields,
                              initialData = {},
                              endpoint,
                              onSuccess,
                              validationRules = {},
                              customValidation = null,
                              customFormContent = null,
                              transformFormData = null,
                              isEdit = false
                          }) => {
    const { token } = useAuth();
    const [formData, setFormData] = useState(initialData);
    const [submitting, setSubmitting] = useState(false);
    const [errors, setErrors] = useState({});

    // Reset form data only when modal opens
    useEffect(() => {
        if (show) {
            setFormData({ ...initialData });
            setErrors({});
        }
    }, [show]);

    // Also reset when modal is hidden
    const handleHide = () => {
        setFormData({ ...initialData });
        setErrors({});
        setSubmitting(false);
        onHide();
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));

        // Clear error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    // Handle react-select changes
    const handleSelectChange = (selectedOption, { name }) => {
        setFormData(prev => ({
            ...prev,
            [name]: selectedOption ? selectedOption.value : ''
        }));

        // Clear error when user makes selection
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    // Custom styles for react-select to match Bootstrap and remove focus outline
    const customSelectStyles = {
        control: (provided, state) => ({
            ...provided,
            borderColor: errors[state.selectProps.name] ? '#dc3545' : '#dee2e6',
            boxShadow: state.isFocused ? '0 0 0 0.2rem rgba(13, 110, 253, 0.25)' : 'none',
            '&:hover': {
                borderColor: errors[state.selectProps.name] ? '#dc3545' : '#86b7fe'
            },
            minHeight: '38px'
        }),
        valueContainer: (provided) => ({
            ...provided,
            padding: '6px 12px'
        }),
        input: (provided) => ({
            ...provided,
            margin: 0,
            padding: 0,
            color: '#212529'
        }),
        placeholder: (provided) => ({
            ...provided,
            color: '#6c757d'
        }),
        singleValue: (provided) => ({
            ...provided,
            color: '#212529'
        }),
        menu: (provided) => ({
            ...provided,
            zIndex: 9999
        }),
        menuPortal: (provided) => ({
            ...provided,
            zIndex: 9999
        })
    };

    const validateForm = () => {
        const newErrors = {};

        // Standard field validation
        fields.forEach(field => {
            if (field.required && !formData[field.name]) {
                newErrors[field.name] = `${field.label} is required`;
            }

            // Individual field validation rules
            if (validationRules[field.name]) {
                const validation = validationRules[field.name](formData[field.name], formData);
                if (!validation.isValid) {
                    newErrors[field.name] = validation.message;
                }
            }
        });

        // Custom validation (gets entire form data)
        if (customValidation) {
            const customErrors = customValidation(formData);
            Object.assign(newErrors, customErrors);
        }

        return newErrors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        const validationErrors = validateForm();
        if (Object.keys(validationErrors).length > 0) {
            setErrors(validationErrors);
            return;
        }

        setSubmitting(true);
        setErrors({});

        try {
            const url = isEdit
                ? `http://localhost:8000/${endpoint}/${initialData.id}/`
                : `http://localhost:8000/${endpoint}/`;

            const method = isEdit ? 'PUT' : 'POST';

            // Transform form data if transformation function is provided
            const dataToSubmit = transformFormData ? transformFormData(formData) : formData;

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(dataToSubmit)
            });

            if (!response.ok) {
                throw new Error(`Failed to ${isEdit ? 'update' : 'create'} ${title.toLowerCase()}`);
            }

            const result = await response.json();
            onSuccess(result);
            handleHide();
        } catch (err) {
            console.error(`Error ${isEdit ? 'updating' : 'creating'} ${title.toLowerCase()}:`, err);
            setErrors({ submit: `Failed to ${isEdit ? 'update' : 'create'} ${title.toLowerCase()}. Please try again.` });
        } finally {
            setSubmitting(false);
        }
    };

    const renderField = (field) => {
        switch (field.type) {
            case 'textarea':
                return (
                    <Form.Control
                        as="textarea"
                        rows={3}
                        name={field.name}
                        value={formData[field.name] || ''}
                        onChange={handleChange}
                        placeholder={field.placeholder}
                        isInvalid={!!errors[field.name]}
                    />
                );

            case 'checkbox':
                return (
                    <Form.Check
                        type="checkbox"
                        name={field.name}
                        checked={formData[field.name] || false}
                        onChange={handleChange}
                        label={field.checkboxLabel || field.label}
                    />
                );

            case 'select':
                return (
                    <Form.Select
                        name={field.name}
                        value={formData[field.name] || ''}
                        onChange={handleChange}
                        isInvalid={!!errors[field.name]}
                    >
                        <option value="">Select {field.label}</option>
                        {field.options?.map(option => (
                            <option key={option.value} value={option.value}>
                                {option.label}
                            </option>
                        ))}
                    </Form.Select>
                );

            case 'react-select':
                const selectedValue = field.options?.find(option => option.value === formData[field.name]);

                return (
                    <Select
                        name={field.name}
                        value={selectedValue || null}
                        onChange={(selectedOption, actionMeta) => handleSelectChange(selectedOption, actionMeta)}
                        options={field.options}
                        placeholder={field.placeholder || `Select ${field.label}`}
                        isSearchable={field.isSearchable !== false}
                        isClearable={field.isClearable}
                        isDisabled={field.isDisabled}
                        styles={customSelectStyles}
                        menuPortalTarget={document.body}
                        className="react-select-container"
                        classNamePrefix="react-select"
                    />
                );

            default:
                return (
                    <Form.Control
                        type={field.type || 'text'}
                        name={field.name}
                        value={formData[field.name] || ''}
                        onChange={handleChange}
                        placeholder={field.placeholder}
                        isInvalid={!!errors[field.name]}
                        step={field.step}
                    />
                );
        }
    };

    return (
        <Modal show={show} onHide={handleHide} size="lg">
            <Modal.Header closeButton>
                <Modal.Title>{isEdit ? 'Edit' : 'Add New'} {title}</Modal.Title>
            </Modal.Header>

            <Form onSubmit={handleSubmit}>
                <Modal.Body>
                    {errors.submit && (
                        <Alert variant="danger">{errors.submit}</Alert>
                    )}

                    {fields.map((field) => (
                        <Form.Group key={field.name} className="mb-3">
                            <Form.Label>
                                {field.label}
                                {field.required && <span className="text-danger">*</span>}
                            </Form.Label>
                            {renderField(field)}
                            {errors[field.name] && (
                                <div className="invalid-feedback d-block">
                                    {errors[field.name]}
                                </div>
                            )}
                        </Form.Group>
                    ))}

                    {/* Render custom form content if provided */}
                    {customFormContent && customFormContent(formData, setFormData, errors)}
                </Modal.Body>

                <Modal.Footer>
                    <div className="modal-buttons-container">
                        <Button
                            variant="secondary"
                            onClick={handleHide}
                        >
                            Cancel
                        </Button>
                        <Button
                            variant="primary"
                            type="submit"
                            disabled={submitting}
                        >
                            {submitting ? (isEdit ? 'Updating...' : 'Saving...') : (isEdit ? 'Update' : 'Save') + " " + title}
                        </Button>
                    </div>
                </Modal.Footer>
            </Form>
        </Modal>
    );
};

export default GenericFormModal;