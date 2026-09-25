import axios from 'axios';
import { supabase } from '../supabase';

// Admin endpoints are verified by the Flask backend against the Supabase
// session, so attach the current access token to every request.
const adminApi = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

adminApi.interceptors.request.use(async (config) => {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
        config.headers['Authorization'] = `Bearer ${session.access_token}`;
    }
    return config;
});

// Normalise backend errors to a readable message
export function errorMessage(error, fallback = 'Une erreur est survenue') {
    return error?.response?.data?.error || error?.message || fallback;
}

export default {
    getOverview() {
        return adminApi.get('/admin/overview').then(r => r.data);
    },

    getUsers(params) {
        return adminApi.get('/admin/users', { params }).then(r => r.data);
    },
    updateUserRole(id, role) {
        return adminApi.patch(`/admin/users/${id}/role`, { role }).then(r => r.data);
    },
    suspendUser(id) {
        return adminApi.post(`/admin/users/${id}/suspend`).then(r => r.data);
    },
    restoreUser(id) {
        return adminApi.post(`/admin/users/${id}/restore`).then(r => r.data);
    },

    getProducts(params) {
        return adminApi.get('/admin/products', { params }).then(r => r.data);
    },
    removeProduct(id, reason) {
        return adminApi.delete(`/admin/products/${id}`, { data: { reason } }).then(r => r.data);
    },

    getMarketPrices(params) {
        return adminApi.get('/market-prices', { params }).then(r => r.data);
    },
    createMarketPrice(payload) {
        return adminApi.post('/admin/market-prices', payload).then(r => r.data);
    },
    deleteMarketPrice(id) {
        return adminApi.delete(`/admin/market-prices/${id}`).then(r => r.data);
    },

    getAuditLog(params) {
        return adminApi.get('/admin/audit-log', { params }).then(r => r.data);
    }
};
