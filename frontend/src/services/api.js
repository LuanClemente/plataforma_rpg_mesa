// frontend/src/services/api.js
// Cliente de API centralizado usando fetch

import API_BASE_URL from '../config/api';

// Função auxiliar para obter o token
const getToken = () => localStorage.getItem('authToken');

// Cliente de API
const api = {
    get: async (endpoint) => {
        const response = await fetch(`${API_BASE_URL}/api${endpoint}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'x-access-token': getToken()
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return { data };
    },

    post: async (endpoint, body) => {
        const response = await fetch(`${API_BASE_URL}/api${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-access-token': getToken()
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return { data };
    },

    put: async (endpoint, body) => {
        const response = await fetch(`${API_BASE_URL}/api${endpoint}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'x-access-token': getToken()
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return { data };
    },

    delete: async (endpoint) => {
        const response = await fetch(`${API_BASE_URL}/api${endpoint}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'x-access-token': getToken()
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return { data };
    }
};

export default api;
