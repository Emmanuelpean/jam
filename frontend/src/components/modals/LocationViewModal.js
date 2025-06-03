import React from 'react';
import { Modal, Button } from 'react-bootstrap';
import LocationMap from '../LocationMap';

const LocationViewModal = ({ show, onHide, location, onEdit }) => {
    // Define view fields for location
    const viewFields = [
        {
            name: 'postcode',
            label: 'Postcode',
            type: 'text'
        },
        {
            name: 'city',
            label: 'City',
            type: 'text'
        },
        {
            name: 'country',
            label: 'Country',
            type: 'text'
        },
        {
            name: 'remote',
            label: 'Remote Work',
            type: 'checkbox'
        }
    ];

    if (!location) return null;

    const renderFieldValue = (field) => {
        const value = location[field.name];

        switch (field.type) {
            case 'checkbox':
                return (
                    <span className={`badge ${value ? 'bg-success' : 'bg-secondary'}`}>
                        {value ? 'Yes' : 'No'}
                    </span>
                );
            default:
                return value || `No ${field.label.toLowerCase()}`;
        }
    };

    return (
        <Modal show={show} onHide={onHide} size="lg">
            <Modal.Header closeButton>
                <Modal.Title>Location Details</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {/* Location Fields */}
                <div className="row mb-4">
                    {viewFields.map((field) => (
                        <div
                            key={field.name}
                            className="col-md-6"
                        >
                            <h6>{field.label}</h6>
                            <p>{renderFieldValue(field)}</p>
                        </div>
                    ))}
                </div>

                {/* Map Section */}
                {!location.remote && (
                    <div className="mb-4">
                        <h6 className="mb-3">
                            📍 Location on Map
                        </h6>
                        <LocationMap
                            locations={[location]}
                            height="300px"
                        />
                    </div>
                )}

                {location.remote && (
                    <div className="mb-4 p-3 bg-light rounded">
                        <div className="text-center">
                            <div className="mb-2" style={{ fontSize: '2rem' }}>🏠</div>
                            <h6 className="text-muted">Remote Location</h6>
                            <p className="text-muted mb-0 small">
                                This location allows remote work and doesn't have a physical address.
                            </p>
                        </div>
                    </div>
                )}

                {/* System fields */}
                <div className="row mt-3 pt-3 border-top">
                    <div className="col-md-6">
                        <h6>Date Added</h6>
                        <p>{new Date(location.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="col-md-6">
                        <h6>Last Updated</h6>
                        <p>{new Date(location.updated_at || location.created_at).toLocaleDateString()}</p>
                    </div>
                </div>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={onHide}>
                    Close
                </Button>
                {onEdit && (
                    <Button
                        variant="primary"
                        onClick={() => {
                            onHide();
                            onEdit(location);
                        }}
                    >
                        Edit Location
                    </Button>
                )}
            </Modal.Footer>
        </Modal>
    );
};

export default LocationViewModal;