import { defineStore } from 'pinia';
import { supabase } from '../supabase';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        userProfile: null,
        session: null,
        isLoading: true,
        error: null
    }),

    getters: {
        isAuthenticated: (state) => !!state.session,
        isFarmer: (state) => state.userProfile?.role === 'farmer',
        isAdmin: (state) => state.userProfile?.role === 'admin'
    },

    actions: {
        // Initialize auth state listener
        async init() {
            try {
                // Get initial session
                const { data: { session } } = await supabase.auth.getSession();
                this.session = session;
                this.user = session?.user || null;

                if (this.user) {
                    await this.fetchUserProfile();
                }

                // Listen for auth changes
                supabase.auth.onAuthStateChange(async (event, session) => {
                    this.session = session;
                    this.user = session?.user || null;

                    if (this.user) {
                        await this.fetchUserProfile();
                    } else {
                        this.userProfile = null;
                    }
                });
            } catch (error) {
                console.error('Auth initialization error:', error);
            } finally {
                this.isLoading = false;
            }
        },

        async fetchUserProfile() {
            if (!this.user) return;

            const { data, error } = await supabase
                .from('users')
                .select('*')
                .eq('id', this.user.id)
                .single();

            if (!error && data) {
                this.userProfile = data;
            }
        },

        async login(credentials) {
            this.isLoading = true;
            this.error = null;
            try {
                const { data, error } = await supabase.auth.signInWithPassword({
                    email: credentials.email,
                    password: credentials.password
                });

                if (error) {
                    this.error = error.message;
                    throw error;
                }

                return data.user;
            } catch (error) {
                this.error = error.message || 'Login failed';
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        async register(userData) {
            this.isLoading = true;
            this.error = null;
            try {
                // Sign up user with Supabase Auth
                const { data: authData, error: authError } = await supabase.auth.signUp({
                    email: userData.email,
                    password: userData.password
                });

                if (authError) {
                    this.error = authError.message;
                    throw authError;
                }

                // Create user profile in users table
                const { error: profileError } = await supabase
                    .from('users')
                    .insert({
                        id: authData.user.id,
                        username: userData.username,
                        email: userData.email,
                        role: userData.role,
                        phone: userData.phone || null,
                        location: userData.location || null
                    });

                if (profileError) {
                    this.error = profileError.message;
                    throw profileError;
                }

                return authData.user;
            } catch (error) {
                console.error('Registration detailed error:', error);
                this.error = error.message || error.error_description || 'Registration failed';
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        async logout() {
            await supabase.auth.signOut();
            this.user = null;
            this.session = null;
            this.userProfile = null;
            this.error = null;
        }
    }
});
