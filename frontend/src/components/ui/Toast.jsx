import React, { useEffect } from 'react';
import { CheckCircle, XCircle, Info, AlertTriangle, X } from 'lucide-react';
import { useToast } from '../../contexts/ToastContext';
import './Toast.css';

const Toast = ({ id, message, type, duration }) => {
    const { removeToast } = useToast();

    // Auto-dismiss is handled in context, but we can also handle it here for pauses on hover (optional enhancement for later)

    const icons = {
        success: <CheckCircle className="toast-icon" size={20} />,
        error: <XCircle className="toast-icon" size={20} />,
        info: <Info className="toast-icon" size={20} />,
        warning: <AlertTriangle className="toast-icon" size={20} />
    };

    return (
        <div className={`toast toast-${type}`}>
            <div className="toast-content">
                {icons[type]}
                <p className="toast-message">{message}</p>
            </div>
            <button className="toast-close" onClick={() => removeToast(id)}>
                <X size={16} />
            </button>
        </div>
    );
};

const ToastContainer = () => {
    const { toasts } = useToast();

    return (
        <div className="toast-container">
            {toasts.map((toast) => (
                <Toast key={toast.id} {...toast} />
            ))}
        </div>
    );
};

export default ToastContainer;
