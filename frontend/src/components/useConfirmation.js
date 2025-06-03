import { useState } from 'react';

export const useConfirmation = () => {
    const [confirmationState, setConfirmationState] = useState({
        show: false,
        title: '',
        message: '',
        confirmText: 'Confirm',
        cancelText: 'Cancel',
        confirmVariant: 'danger',
        icon: null,
        onConfirm: null
    });

    const showConfirmation = ({
                                  title = 'Confirm Action',
                                  message = 'Are you sure you want to proceed?',
                                  confirmText = 'Confirm',
                                  cancelText = 'Cancel',
                                  confirmVariant = 'danger',
                                  icon = null,
                                  onConfirm
                              }) => {
        return new Promise((resolve) => {
            setConfirmationState({
                show: true,
                title,
                message,
                confirmText,
                cancelText,
                confirmVariant,
                icon,
                onConfirm: () => {
                    resolve(true);
                    onConfirm && onConfirm();
                }
            });
        });
    };

    const hideConfirmation = () => {
        setConfirmationState(prev => ({ ...prev, show: false }));
    };

    return {
        confirmationState,
        showConfirmation,
        hideConfirmation
    };
};