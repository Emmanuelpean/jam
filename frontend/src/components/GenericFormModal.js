import React, {useEffect, useState} from 'react';
import {Alert, Button, Form, Modal} from 'react-bootstrap';
import {useAuth} from '../contexts/AuthContext';
import './GenericFormModal.css'; // Add this import

const GenericFormModal = ({
                              show,
                              onHide,
                              title,
                              fields,
                              initialData = {},
                              endpoint,
                              onSuccess,
                              validationRules = {}
                          }) => {
    const {token} = useAuth();
    const [formData, setFormData] = useState(initialData);
    const [submitting, setSubmitting] = useState(false);
    const [errors, setErrors] = useState({});

    // Reset form data only when modal opens (show changes from false to true)
    useEffect(() => {
        if (show) {
            // Reset form when modal opens
            setFormData({...initialData});
            setErrors({});
        }
    }, [show]); // Remove initialData from dependencies

    // Also reset when modal is hidden
    const handleHide = () => {
        setFormData({...initialData});
        setErrors({});
        setSubmitting(false);
        onHide();
    };

    const handleChange = (e) => {
        const {name, value, type, checked} = e.target;
        setFormData(prev => ({
            ...prev, [name]: type === 'checkbox' ? checked : value
        }));

        // Clear error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({...prev, [name]: ''}));
        }
    };

    const validateForm = () => {
        const newErrors = {};

        fields.forEach(field => {
            if (field.required && !formData[field.name]) {
                newErrors[field.name] = `${field.label} is required`;
            }

            if (validationRules[field.name]) {
                const validation = validationRules[field.name](formData[field.name]);
                if (!validation.isValid) {
                    newErrors[field.name] = validation.message;
                }
            }
        });

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
            const response = await fetch(`http://localhost:8000/${endpoint}/`, {
                method: 'POST', headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`Failed to create ${title.toLowerCase()}`);
            }

            const result = await response.json();
            onSuccess(result);
            handleHide(); // Use handleHide instead of onHide to reset form
        } catch (err) {
            console.error(`Error creating ${title.toLowerCase()}:`, err);
            setErrors({submit: `Failed to create ${title.toLowerCase()}. Please try again.`});
        } finally {
            setSubmitting(false);
        }
    };

    const renderField = (field) => {
        switch (field.type) {
            case 'textarea':
                return (<Form.Control
                    as="textarea"
                    rows={3}
                    name={field.name}
                    value={formData[field.name] || ''}
                    onChange={handleChange}
                    placeholder={field.placeholder}
                    isInvalid={!!errors[field.name]}
                />);

            case 'checkbox':
                return (<Form.Check
                    type="checkbox"
                    name={field.name}
                    checked={formData[field.name] || false}
                    onChange={handleChange}
                    label={field.checkboxLabel || field.label}
                />);

            case 'select':
                return (<Form.Select
                    name={field.name}
                    value={formData[field.name] || ''}
                    onChange={handleChange}
                    isInvalid={!!errors[field.name]}
                >
                    <option value="">Select {field.label}</option>
                    {field.options?.map(option => (<option key={option.value} value={option.value}>
                        {option.label}
                    </option>))}
                </Form.Select>);

            default:
                return (<Form.Control
                    type={field.type || 'text'}
                    name={field.name}
                    value={formData[field.name] || ''}
                    onChange={handleChange}
                    placeholder={field.placeholder}
                    isInvalid={!!errors[field.name]}
                />);
        }
    };

    return (
        <Modal show={show} onHide={handleHide} size="lg">
            <Modal.Header closeButton>
                <Modal.Title>Add New {title}</Modal.Title>
            </Modal.Header>

            <Form onSubmit={handleSubmit}>
                <Modal.Body>
                    {errors.submit && (<Alert variant="danger">{errors.submit}</Alert>)}

                    {fields.map((field) => (<Form.Group key={field.name} className="mb-3">
                        <Form.Label>
                            {field.label}
                            {field.required && <span className="text-danger">*</span>}
                        </Form.Label>
                        {renderField(field)}
                        {errors[field.name] && (<Form.Control.Feedback type="invalid">
                            {errors[field.name]}
                        </Form.Control.Feedback>)}
                    </Form.Group>))}
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
                            {submitting ? 'Saving...' : "Save " + title}
                        </Button></div>
                </Modal.Footer>
            </Form>
        </Modal>);
};

export default GenericFormModal;