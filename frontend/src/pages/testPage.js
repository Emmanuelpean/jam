import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Modal, Form, Alert } from 'react-bootstrap';
import Select from 'react-select';
import '../index.css';

const StyleShowcase = () => {
    const [showModal, setShowModal] = useState(false);
    const [formData, setFormData] = useState({
        textInput: '',
        emailInput: '',
        passwordInput: '',
        urlInput: '',
        numberInput: '',
        dateInput: '',
        textareaInput: '',
        selectInput: '',
        checkboxInput: false,
        rangeInput: 3,
        reactSelectInput: ''
    });
    const [errors, setErrors] = useState({});
    const [showErrorStates, setShowErrorStates] = useState(false);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSelectChange = (selectedOption) => {
        setFormData(prev => ({
            ...prev,
            reactSelectInput: selectedOption ? selectedOption.value : ''
        }));
    };

    const toggleErrorStates = () => {
        if (!showErrorStates) {
            setErrors({
                textInput: 'This field is required',
                emailInput: 'Please enter a valid email address',
                numberInput: 'Value must be between 1 and 100',
                selectInput: 'Please select an option'
            });
        } else {
            setErrors({});
        }
        setShowErrorStates(!showErrorStates);
    };

    const selectOptions = [
        { value: 'option1', label: 'Option 1' },
        { value: 'option2', label: 'Option 2' },
        { value: 'option3', label: 'Option 3' },
        { value: 'option4', label: 'Very Long Option Name That Might Wrap' },
        { value: 'option5', label: 'Another Option' }
    ];

    const customSelectStyles = {
        control: (provided, state) => ({
            ...provided,
            borderColor: errors.reactSelectInput ? '#dc3545' : '#dee2e6',
            boxShadow: state.isFocused ? '0 0 0 0.2rem rgba(13, 110, 253, 0.25)' : 'none',
            '&:hover': {
                borderColor: errors.reactSelectInput ? '#dc3545' : '#86b7fe'
            },
            minHeight: '48px'
        }),
        valueContainer: (provided) => ({
            ...provided,
            padding: '0.375rem 0.75rem'
        }),
        input: (provided) => ({
            ...provided,
            margin: 0,
            padding: 0,
            color: '#212529'
        }),
        placeholder: (provided) => ({
            ...provided,
            color: '#6c757d',
            fontStyle: 'italic'
        }),
        singleValue: (provided) => ({
            ...provided,
            color: '#212529'
        }),
        menu: (provided) => ({
            ...provided,
            zIndex: 9999
        })
    };

    return (
        <Container fluid className="py-4">
            <Row className="justify-content-center">
                <Col lg={10}>
                    <Card className="shadow-lg">
                        <Card.Header className="bg-primary text-white">
                            <h2 className="mb-0">Form Styles Showcase</h2>
                            <p className="mb-0 mt-2 opacity-75">
                                Comprehensive demonstration of all form styling components
                            </p>
                        </Card.Header>
                        <Card.Body className="p-4">
                            {/* Control Buttons */}
                            <Row className="mb-4">
                                <Col>
                                    <div className="d-flex gap-3 flex-wrap">
                                        <Button
                                            variant="primary"
                                            onClick={() => setShowModal(true)}
                                        >
                                            Open Modal Example
                                        </Button>
                                        <Button
                                            variant={showErrorStates ? "success" : "warning"}
                                            onClick={toggleErrorStates}
                                        >
                                            {showErrorStates ? "Hide" : "Show"} Error States
                                        </Button>
                                        <Button variant="secondary" disabled>
                                            Disabled Button
                                        </Button>
                                    </div>
                                </Col>
                            </Row>

                            {/* Alert Examples */}
                            <Row className="mb-4">
                                <Col>
                                    <h4 className="mb-3">Alert Components</h4>
                                    <Alert variant="danger">
                                        <strong>Error:</strong> This is how error messages appear in forms.
                                    </Alert>
                                    <Alert variant="success">
                                        <strong>Success:</strong> Form submitted successfully!
                                    </Alert>
                                    <Alert variant="warning">
                                        <strong>Warning:</strong> Please review your input before proceeding.
                                    </Alert>
                                </Col>
                            </Row>

                            {/* Form Elements */}
                            <Row>
                                <Col lg={6}>
                                    <h4 className="mb-3">Text Input Fields</h4>

                                    <Form.Group className="mb-3">
                                        <Form.Label>
                                            Standard Text Input
                                            <span className="text-danger">*</span>
                                        </Form.Label>
                                        <Form.Control
                                            type="text"
                                            name="textInput"
                                            value={formData.textInput}
                                            onChange={handleChange}
                                            placeholder="Enter some text..."
                                            isInvalid={!!errors.textInput}
                                        />
                                        {errors.textInput && (
                                            <div className="invalid-feedback">
                                                {errors.textInput}
                                            </div>
                                        )}
                                    </Form.Group>

                                    <Form.Group className="mb-3">
                                        <Form.Label>Email Input</Form.Label>
                                        <Form.Control
                                            type="email"
                                            name="emailInput"
                                            value={formData.emailInput}
                                            onChange={handleChange}
                                            placeholder="your.email@example.com"
                                            isInvalid={!!errors.emailInput}
                                        />
                                        {errors.emailInput && (
                                            <div className="invalid-feedback">
                                                {errors.emailInput}
                                            </div>
                                        )}
                                    </Form.Group>

                                    <Form.Group className="mb-3">
                                        <Form.Label>Password Input</Form.Label>
                                        <Form.Control
                                            type="password"
                                            name="passwordInput"
                                            value={formData.passwordInput}
                                            onChange={handleChange}
                                            placeholder="Enter password..."
                                        />
                                    </Form.Group>

                                    <Form.Group className="mb-3">
                                        <Form.Label>URL Input</Form.Label>
                                        <Form.Control
                                            type="url"
                                            name="urlInput"
                                            value={formData.urlInput}
                                            onChange={handleChange}
                                            placeholder="https://example.com"
                                        />
                                    </Form.Group>

                                    <Form.Group className="mb-3">
                                        <Form.Label>Number Input</Form.Label>
                                        <Form.Control
                                            type="number"
                                            name="numberInput"
                                            value={formData.numberInput}
                                            onChange={handleChange}
                                            placeholder="Enter a number..."
                                            min="1"
                                            max="100"
                                            isInvalid={!!errors.numberInput}
                                        />
                                        {errors.numberInput && (
                                            <div className="invalid-feedback">
                                                {errors.numberInput}
                                            </div>
                                        )}
                                    </Form.Group>

                                    <Form.Group className="mb-3">
                                        <Form.Label>Date Input</Form.Label>
                                        <Form.Control
                                            type="date"
                                            name="dateInput"
                                            value={formData.dateInput}
                                            onChange={handleChange}
                                        />
                                    </Form.Group>
                                </Col>

                                <Col lg={6}>
                                    <h4 className="mb-3">Advanced Input Fields</h4>

                                    <Form.Group className="mb-3">
                                        <Form.Label>Textarea</Form.Label>
                                        <Form.Control
                                            as="textarea"
                                            rows={4}
                                            name="textareaInput"
                                            value={formData.textareaInput}
                                            onChange={handleChange}
                                            placeholder="Enter a longer description here..."
                                        />
                                    </Form.Group>

                                    <Form.Group className="mb-3">
                                        <Form.Label>Standard Select</Form.Label>
                                        <Form.Select
                                            name="selectInput"
                                            value={formData.selectInput}
                                            onChange={handleChange}
                                            isInvalid={!!errors.selectInput}
                                        >
                                            <option value="">Choose an option...</option>
                                            <option value="option1">Option 1</option>
                                            <option value="option2">Option 2</option>
                                            <option value="option3">Option 3</option>
                                        </Form.Select>
                                        {errors.selectInput && (
                                            <div className="invalid-feedback">
                                                {errors.selectInput}
                                            </div>
                                        )}
                                    </Form.Group>

                                    <Form.Group className="mb-3">
                                        <Form.Label>React Select (Searchable)</Form.Label>
                                        <Select
                                            value={selectOptions.find(option => option.value === formData.reactSelectInput)}
                                            onChange={handleSelectChange}
                                            options={selectOptions}
                                            placeholder="Search and select an option..."
                                            isSearchable={true}
                                            isClearable={true}
                                            styles={customSelectStyles}
                                            className="react-select-container"
                                            classNamePrefix="react-select"
                                        />
                                        {errors.reactSelectInput && (
                                            <div className="invalid-feedback d-block">
                                                {errors.reactSelectInput}
                                            </div>
                                        )}
                                    </Form.Group>

                                    <Form.Group className="mb-3">
                                        <Form.Check
                                            type="checkbox"
                                            name="checkboxInput"
                                            checked={formData.checkboxInput}
                                            onChange={handleChange}
                                            label="I agree to the terms and conditions"
                                        />
                                    </Form.Group>

                                    <Form.Group className="mb-3">
                                        <Form.Label>
                                            Range Slider (Value: {formData.rangeInput})
                                        </Form.Label>
                                        <Form.Range
                                            name="rangeInput"
                                            value={formData.rangeInput}
                                            onChange={handleChange}
                                            min="1"
                                            max="5"
                                        />
                                        <div className="d-flex justify-content-between small text-muted">
                                            <span>1</span>
                                            <span>2</span>
                                            <span>3</span>
                                            <span>4</span>
                                            <span>5</span>
                                        </div>
                                    </Form.Group>

                                    <div className="bg-light p-3 rounded">
                                        <h6>Inline Form Section</h6>
                                        <Form.Group className="mb-2">
                                            <Form.Label>Quick Add Field</Form.Label>
                                            <Form.Control
                                                type="text"
                                                placeholder="Add something quickly..."
                                                size="sm"
                                            />
                                        </Form.Group>
                                        <Button variant="outline-primary" size="sm">
                                            + Add Item
                                        </Button>
                                    </div>
                                </Col>
                            </Row>

                            {/* Button Examples */}
                            <Row className="mt-4">
                                <Col>
                                    <h4 className="mb-3">Button Variations</h4>
                                    <div className="d-flex gap-2 flex-wrap">
                                        <Button variant="primary">Primary Button</Button>
                                        <Button variant="secondary">Secondary Button</Button>
                                        <Button variant="success">Success Button</Button>
                                        <Button variant="warning">Warning Button</Button>
                                        <Button variant="danger">Danger Button</Button>
                                        <Button variant="outline-primary">Outline Primary</Button>
                                        <Button variant="link">Link Button</Button>
                                    </div>
                                </Col>
                            </Row>

                            {/* Loading State Example */}
                            <Row className="mt-4">
                                <Col>
                                    <h4 className="mb-3">Loading States</h4>
                                    <div className="d-flex gap-2 align-items-center">
                                        <Button variant="primary" disabled>
                                            <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                                            Loading...
                                        </Button>
                                        <div className="spinner-border text-primary" role="status">
                                            <span className="visually-hidden">Loading...</span>
                                        </div>
                                    </div>
                                </Col>
                            </Row>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            {/* Modal Example */}
            <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
                <Modal.Header closeButton>
                    <Modal.Title>Modal Form Example</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Alert variant="info">
                        This modal demonstrates how all the form styles look within the modal context.
                    </Alert>

                    <Form>
                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>
                                        Full Name
                                        <span className="text-danger">*</span>
                                    </Form.Label>
                                    <Form.Control
                                        type="text"
                                        placeholder="Enter your full name..."
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Email Address</Form.Label>
                                    <Form.Control
                                        type="email"
                                        placeholder="your.email@example.com"
                                    />
                                </Form.Group>
                            </Col>
                        </Row>

                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Department</Form.Label>
                                    <Select
                                        options={[
                                            { value: 'engineering', label: 'Engineering' },
                                            { value: 'design', label: 'Design' },
                                            { value: 'marketing', label: 'Marketing' },
                                            { value: 'sales', label: 'Sales' }
                                        ]}
                                        placeholder="Select department..."
                                        isSearchable={true}
                                        isClearable={true}
                                        styles={customSelectStyles}
                                        className="react-select-container"
                                        classNamePrefix="react-select"
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Start Date</Form.Label>
                                    <Form.Control type="date" />
                                </Form.Group>
                            </Col>
                        </Row>

                        <Form.Group className="mb-3">
                            <Form.Label>Bio</Form.Label>
                            <Form.Control
                                as="textarea"
                                rows={3}
                                placeholder="Tell us about yourself..."
                            />
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Check
                                type="checkbox"
                                label="I want to receive email notifications"
                            />
                        </Form.Group>

                        <div className="bg-light p-3 rounded">
                            <h6>Additional Information</h6>
                            <Form.Group className="mb-2">
                                <Form.Label>Emergency Contact</Form.Label>
                                <Form.Control
                                    type="text"
                                    placeholder="Emergency contact name..."
                                />
                            </Form.Group>
                            <Button variant="outline-secondary" size="sm">
                                + Add Another Contact
                            </Button>
                        </div>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <div className="modal-buttons-container">
                        <Button variant="secondary" onClick={() => setShowModal(false)}>
                            Cancel
                        </Button>
                        <Button variant="primary">
                            Save Changes
                        </Button>
                    </div>
                </Modal.Footer>
            </Modal>
        </Container>
    );
};

export default StyleShowcase;