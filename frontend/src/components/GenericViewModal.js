import React from 'react';
import { Modal, Button } from 'react-bootstrap';

const GenericViewModal = ({
                              show,
                              onHide,
                              title,
                              data,
                              fields,
                              onEdit,
                              showEditButton = true
                          }) => {
    if (!data) return null;

    const renderFieldValue = (field) => {
        const value = data[field.name];

        switch (field.type) {
            case 'checkbox':
                return (
                    <span className={`badge ${value ? 'bg-success' : 'bg-secondary'}`}>
                        {value ? 'Yes' : 'No'}
                    </span>
                );

            case 'url':
                return value ? (
                    <a href={value} target="_blank" rel="noopener noreferrer">
                        {value}
                    </a>
                ) : 'No URL provided';

            case 'textarea':
                return value || `No ${field.label.toLowerCase()}`;

            case 'select':
                // Find the option label if options are provided
                if (field.options) {
                    const option = field.options.find(opt => opt.value === value);
                    return option ? option.label : value || `No ${field.label.toLowerCase()}`;
                }
                return value || `No ${field.label.toLowerCase()}`;

            default:
                return value || `No ${field.label.toLowerCase()}`;
        }
    };

    return (
        <Modal show={show} onHide={onHide} size="lg">
            <Modal.Header closeButton>
                <Modal.Title>{title} Details</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <div className="row">
                    {fields.map((field, index) => (
                        <div
                            key={field.name}
                            className={field.type === 'textarea' ? 'col-12' : 'col-md-6'}
                        >
                            <h6>{field.label}</h6>
                            <p>{renderFieldValue(field)}</p>
                        </div>
                    ))}
                </div>

                {/* System fields */}
                <div className="row mt-3 pt-3 border-top">
                    <div className="col-md-6">
                        <h6>Date Added</h6>
                        <p>{new Date(data.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="col-md-6">
                        <h6>Last Updated</h6>
                        <p>{new Date(data.updated_at || data.created_at).toLocaleDateString()}</p>
                    </div>
                </div>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={onHide}>
                    Close
                </Button>
                {showEditButton && onEdit && (
                    <Button
                        variant="primary"
                        onClick={() => {
                            onHide();
                            onEdit(data);
                        }}
                    >
                        Edit {title}
                    </Button>
                )}
            </Modal.Footer>
        </Modal>
    );
};

export default GenericViewModal;