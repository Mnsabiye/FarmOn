import './style.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize Supabase auth listener
// Initialize Supabase auth listener
const authStore = useAuthStore()

// Wait for auth to initialize before mounting to prevent redirecting logged-in users
const initApp = async () => {
    await authStore.init()
    app.mount('#app')
}

initApp()
