import React, { createContext, useContext, useState, useCallback } from 'react';


const ToastContext = createContext();

export const useToast = () => {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within a ToastProvider');
    }
    return context;
};

export const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);

    const addToast = useCallback((message, type = 'info', duration = 5000) => {
        const id = Date.now().toString() + Math.random().toString(36).substring(2);
        setToasts((prev) => [...prev, { id, message, type, duration }]);

        if (duration) {
            setTimeout(() => {
                removeToast(id);
            }, duration);
        }
    }, []);

    const removeToast = useCallback((id) => {
        setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, []);

    const success = useCallback((message, duration) => addToast(message, 'success', duration), [addToast]);
    const error = useCallback((message, duration) => addToast(message, 'error', duration), [addToast]);
    const info = useCallback((message, duration) => addToast(message, 'info', duration), [addToast]);
    const warning = useCallback((message, duration) => addToast(message, 'warning', duration), [addToast]);

    return (
        <ToastContext.Provider value={{ toasts, removeToast, success, error, info, warning }}>
            {children}
        </ToastContext.Provider>
    );
};
