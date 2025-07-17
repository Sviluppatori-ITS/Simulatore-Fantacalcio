export async function apiFetch(input: RequestInfo, init?: RequestInit) {
    const accessToken = localStorage.getItem('token');
    const refreshToken = localStorage.getItem('refresh_token');
    const headers = new Headers(init?.headers);

    if (accessToken) {
        headers.set('Authorization', `Bearer ${accessToken}`);
    }

    let response = await fetch(input, {
        ...init,
        headers,
    });

    if (response.status === 401 && refreshToken) {
        // Provo a fare refresh del token
        const refreshResponse = await fetch('/api/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        if (!refreshResponse.ok) {
            // Refresh fallito, logout
            localStorage.removeItem('token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
            throw new Error('Session expired. Please login again.');
        }

        const data = await refreshResponse.json();
        const newAccessToken = data.access;

        // Salvo nuovo access token
        localStorage.setItem('token', newAccessToken);

        // Rifaccio la chiamata originale con il nuovo token
        headers.set('Authorization', `Bearer ${newAccessToken}`);

        response = await fetch(input, {
            ...init,
            headers,
        });
    }

    if (response.status === 401) {
        // Se ancora 401, logout
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        throw new Error('Unauthorized');
    }

    return response;
}
