// src/hooks/useAlert.js
import { useState } from 'react';

export const useAlert = () => {
    const [alertState, setAlertState] = useState({
        show: false,
        title: 'Alert',
        message: '',
        type: 'info',
        confirmText: 'OK',
        icon: null,
        size: 'md',
        onConfirm: null
    });

    const showAlert = ({
        title = 'Alert',
        message,
        type = 'info',
        confirmText = 'OK',
        icon = null,
        size = 'md',
        onConfirm = null
    }) => {
        return new Promise((resolve) => {
            setAlertState({
                show: true,
                title,
                message,
                type,
                confirmText,
                icon,
                size,
                onConfirm: () => {
                    if (onConfirm) onConfirm();
                    resolve(true);
                    hideAlert();
                }
            });
        });
    };

    const hideAlert = () => {
        setAlertState(prev => ({
            ...prev,
            show: false
        }));
    };

    return {
        alertState,
        showAlert,
        hideAlert
    };
};