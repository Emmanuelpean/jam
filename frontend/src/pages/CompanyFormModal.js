import React, {useState} from 'react';
import {Button, Form, Modal} from 'react-bootstrap';
import '../App.css';


const CompanyFormModal = ({
                              showCompanyModal,
                              setShowCompanyModal,
                              companyFormData,
                              handleCompanyChange,
                              handleCompanySubmit,
                              formErrors,
                              submitting
                          }) => {
    const [touched, setTouched] = useState({});

    const handleBlur = (e) => {
        const {name} = e.target;
        setTouched(prev => ({...prev, [name]: true}));
    };

    const isFieldInvalid = (fieldName) => {
        return touched[fieldName] && !companyFormData[fieldName];
    };

    const onSubmit = (e) => {
        e.preventDefault();
        // Mark all fields as touched when submitting
        const newTouched = {};
        Object.keys(companyFormData).forEach(key => {
            newTouched[key] = true;
        });
        setTouched(newTouched);

        if (e.currentTarget.checkValidity()) {
            handleCompanySubmit(e);
        }
    };

    return (
        <Modal show={showCompanyModal} onHide={() => setShowCompanyModal(false)}>
            <Modal.Header closeButton>
                <Modal.Title>Add New Company</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Form onSubmit={onSubmit}>
                    <Form.Group className="mb-3">
                        <Form.Label>Company Name</Form.Label>
                        <Form.Control
                            type="text"
                            name="name"
                            value={companyFormData.name}
                            onChange={handleCompanyChange}
                            onBlur={handleBlur}
                            required
                            className={isFieldInvalid('name') ? 'is-invalid' : ''}
                        />
                        <div className="invalid-feedback">
                            Please enter a company name
                        </div>
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Website</Form.Label>
                        <Form.Control
                            type="url"
                            name="website"
                            value={companyFormData.website}
                            onChange={handleCompanyChange}
                        />
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Notes</Form.Label>
                        <Form.Control
                            as="textarea"
                            name="notes"
                            value={companyFormData.notes}
                            onChange={handleCompanyChange}
                            rows={3}
                        />
                    </Form.Group>

                    {formErrors.company && (
                        <div className="alert alert-danger">{formErrors.company}</div>
                    )}

                    <div className="d-flex justify-content-end">
                        <Button variant="secondary" onClick={() => setShowCompanyModal(false)} className="me-2">
                            Cancel
                        </Button>
                        <Button variant="primary" type="submit" disabled={submitting}>
                            {submitting ? 'Saving...' : 'Save Company'}
                        </Button>
                    </div>
                </Form>
            </Modal.Body>
        </Modal>
    );
};

export default CompanyFormModal;