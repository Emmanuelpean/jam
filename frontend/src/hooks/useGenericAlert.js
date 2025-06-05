
import { useState } from 'react';

export const useGenericAlert = () => {
    const [alertState, setAlertState] = useState({
        show: false,
        title: 'Alert',
        message: '',
        type: 'info',
        confirmText: 'OK',
        icon: null,
        size: 'md',
        onSuccess: null
    });

    const showAlert = ({
                           title = 'Alert',
                           message,
                           type = 'info',
                           confirmText = 'OK',
                           icon = null,
                           size = 'md',
                           onSuccess = null
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
                onSuccess: () => {
                    if (onSuccess) onSuccess();
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