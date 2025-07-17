import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Logout() {
    const navigate = useNavigate();

    React.useEffect(() => {
        localStorage.removeItem('token');
        navigate('/login');
    }, [navigate]);

    return <p>Logging out...</p>;
}
