import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

const ProtectedRoute: React.FC = () => {
    const token = localStorage.getItem('token');

    if (!token) {
        // Se non c'è token, reindirizza al login
        return <Navigate to="/login" replace />;
    }

    // Se c'è token, mostra la pagina richiesta (figli della route)
    return <Outlet />;
};

export default ProtectedRoute;
