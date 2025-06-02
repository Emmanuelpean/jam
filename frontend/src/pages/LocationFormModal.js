
import React, { useState } from 'react';
import { Button, Form, Modal } from 'react-bootstrap';

const LocationFormModal = ({
                               showLocationModal,
                               setShowLocationModal,
                               handleLocationSubmit,
                               formErrors,
                               submitting
                           }) => {
    const [locationFormData, setLocationFormData] = useState({
        city: '',
        state: '',
        country: '',
        remote: false
    });

    const [touched, setTouched] = useState({});

    const handleLocationChange = (e) => {
        const { name, value, type, checked } = e.target;
        setLocationFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleBlur = (e) => {
        const { name } = e.target;
        setTouched(prev => ({ ...prev, [name]: true }));
    };

    const isFieldInvalid = (fieldName) => {
        return touched[fieldName] && !locationFormData[fieldName];
    };

    const onSubmit = (e) => {
        e.preventDefault();
        const newTouched = {};
        Object.keys(locationFormData).forEach(key => {
            newTouched[key] = true;
        });
        setTouched(newTouched);

        if (e.currentTarget.checkValidity()) {
            handleLocationSubmit(e, locationFormData);
        }
    };

    return (
        <Modal show={showLocationModal} onHide={() => setShowLocationModal(false)}>
            <Modal.Header closeButton>
                <Modal.Title>Add New Location</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Form onSubmit={onSubmit}>
                    <Form.Group className="mb-3">
                        <Form.Label>City</Form.Label>
                        <Form.Control
                            type="text"
                            name="city"
                            value={locationFormData.city}
                            onChange={handleLocationChange}
                            onBlur={handleBlur}
                            required
                            className={isFieldInvalid('city') ? 'is-invalid' : ''}
                        />
                        <div className="invalid-feedback">
                            Please enter a city
                        </div>
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>State/Province</Form.Label>
                        <Form.Control
                            type="text"
                            name="state"
                            value={locationFormData.state}
                            onChange={handleLocationChange}
                        />
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Country</Form.Label>
                        <Form.Control
                            type="text"
                            name="country"
                            value={locationFormData.country}
                            onChange={handleLocationChange}
                        />
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Check
                            type="checkbox"
                            label="Remote position"
                            name="remote"
                            checked={locationFormData.remote}
                            onChange={handleLocationChange}
                        />
                    </Form.Group>

                    {formErrors.location && (
                        <div className="alert alert-danger">{formErrors.location}</div>
                    )}

                    <div className="d-flex justify-content-end">
                        <Button variant="secondary" onClick={() => setShowLocationModal(false)} className="me-2">
                            Cancel
                        </Button>
                        <Button variant="primary" type="submit" disabled={submitting}>
                            {submitting ? 'Saving...' : 'Save Location'}
                        </Button>
                    </div>
                </Form>
            </Modal.Body>
        </Modal>
    );
};

export default LocationFormModal;