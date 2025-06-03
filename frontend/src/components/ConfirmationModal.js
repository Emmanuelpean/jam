import React from 'react';
import { Modal, Button } from 'react-bootstrap';

const ConfirmationModal = ({
                               show,
                               onHide,
                               onConfirm,
                               title = 'Confirm Action',
                               message = 'Are you sure you want to proceed?',
                               confirmText = 'Confirm',
                               cancelText = 'Cancel',
                               confirmVariant = 'danger',
                               icon = null
                           }) => {
    const handleConfirm = () => {
        onConfirm();
        onHide();
    };

    return (
        <Modal show={show} onHide={onHide} centered>
            <Modal.Header closeButton>
                <Modal.Title className="d-flex align-items-center">
                    {icon && <span className="me-2">{icon}</span>}
                    {title}
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <p className="mb-0">{message}</p>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={onHide}>
                    {cancelText}
                </Button>
                <Button variant={confirmVariant} onClick={handleConfirm}>
                    {confirmText}
                </Button>
            </Modal.Footer>
        </Modal>
    );
};

export default ConfirmationModal;