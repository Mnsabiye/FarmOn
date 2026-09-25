import { watch } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: () => import('../views/LandingPage.vue')
        },
        {
            path: '/marketplace',
            name: 'marketplace',
            component: () => import('../views/Marketplace.vue')
        },
        {
            path: '/login',
            name: 'login',
            component: () => import('../views/LoginPage.vue'),
            meta: { guest: true }
        },
        {
            path: '/register',
            name: 'register',
            component: () => import('../views/RegisterPage.vue'),
            meta: { guest: true }
        },
        {
            path: '/dashboard',
            name: 'dashboard',
            component: () => import('../views/FarmerDashboard.vue'),
            meta: { requiresAuth: true, requiresFarmer: true }
        },
        {
            path: '/admin',
            name: 'admin',
            component: () => import('../views/AdminDashboard.vue'),
            meta: { requiresAuth: true, requiresAdmin: true }
        }
    ]
});

// The router starts its first navigation as soon as it is installed, before
// authStore.init() has restored the session. Wait for it, otherwise a page
// refresh on a protected route redirects a logged-in user to /login.
const authReady = (authStore) => {
    if (!authStore.isLoading) return Promise.resolve();
    return new Promise((resolve) => {
        const stop = watch(() => authStore.isLoading, (loading) => {
            if (!loading) {
                stop();
                resolve();
            }
        });
    });
};

router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore();
    await authReady(authStore);
    const isAuthenticated = authStore.isAuthenticated;
    const isFarmer = authStore.isFarmer;
    const isAdmin = authStore.isAdmin;

    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login');
    } else if (to.meta.requiresFarmer && !isFarmer) {
        next('/'); // Or unauthorized page
    } else if (to.meta.requiresAdmin && !isAdmin) {
        next('/');
    } else if (to.meta.guest && isAuthenticated) {
        next(isAdmin ? '/admin' : '/dashboard');
    } else {
        next();
    }
});

export default router;
