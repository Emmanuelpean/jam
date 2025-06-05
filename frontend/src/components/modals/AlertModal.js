import React from 'react';
import { Modal, Button } from 'react-bootstrap';

const AlertModal = ({
                        show,
                        onHide,
                        title = 'Alert',
                        message,
                        type = 'info', // 'info', 'success', 'warning', 'error'
                        confirmText = 'OK',
                        icon = null,
                        size = 'md' // 'sm', 'md', 'lg'
                    }) => {
    const getTypeVariant = (type) => {
        switch (type) {
            case 'success':
                return 'success';
            case 'warning':
                return 'warning';
            case 'error':
                return 'danger';
            default:
                return 'primary';
        }
    };

    const getDefaultIcon = (type) => {
        switch (type) {
            case 'success':
                return '✅';
            case 'warning':
                return '⚠️';
            case 'error':
                return '❌';
            default:
                return 'ℹ️';
        }
    };

    const displayIcon = icon || getDefaultIcon(type);

    return (
        <Modal
            show={show}
            onHide={onHide}
            centered
            size={size}
            backdrop="static"
            keyboard={false}
        >
            <Modal.Header closeButton className={`bg-${getTypeVariant(type)} bg-opacity-10`}>
                <Modal.Title className="d-flex align-items-center">
                    {displayIcon && <span className="me-2" style={{ fontSize: '1.2em' }}>{displayIcon}</span>}
                    {title}
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <div className="text-center py-3">
                    {typeof message === 'string' ? (
                        <p className="mb-0">{message}</p>
                    ) : (
                        message
                    )}
                </div>
            </Modal.Body>
            <Modal.Footer className="justify-content-center">
                <Button
                    variant={getTypeVariant(type)}
                    onClick={onHide}
                    size="lg"
                    style={{ minWidth: '100px' }}
                >
                    {confirmText}
                </Button>
            </Modal.Footer>
        </Modal>
    );
};

export default AlertModal;