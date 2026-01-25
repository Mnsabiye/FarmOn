import { defineStore } from 'pinia';
import { supabase } from '../supabase';

export const useProductStore = defineStore('products', {
    state: () => ({
        products: [],
        currentProduct: null,
        isLoading: false,
        error: null,
        filters: {
            category: ''
        }
    }),

    getters: {
        filteredProducts: (state) => {
            let filtered = state.products;

            if (state.filters.category) {
                filtered = filtered.filter(p => p.category === state.filters.category);
            }

            return filtered;
        }
    },

    actions: {
        async fetchProducts(params = {}) {
            this.isLoading = true;
            this.error = null;
            try {
                let query = supabase
                    .from('products')
                    .select(`
                        *,
                        farmer:users!farmer_id (username, phone, location)
                    `)
                    .order('created_at', { ascending: false });

                // Apply filters if provided
                if (params.category) {
                    query = query.eq('category', params.category);
                }

                if (params.farmerId) {
                    query = query.eq('farmer_id', params.farmerId);
                }

                const { data, error } = await query;

                if (error) throw error;

                // Transform data to match expected format
                this.products = data.map(product => ({
                    ...product,
                    farmer_name: product.farmer?.username,
                    farmer_phone: product.farmer?.phone,
                    farmer_location: product.farmer?.location
                }));
            } catch (error) {
                this.error = error.message || 'Failed to fetch products';
            } finally {
                this.isLoading = false;
            }
        },

        async fetchProduct(id) {
            this.isLoading = true;
            this.error = null;
            try {
                const { data, error } = await supabase
                    .from('products')
                    .select(`
                        *,
                        farmer:users!farmer_id (username, phone, location)
                    `)
                    .eq('id', id)
                    .single();

                if (error) throw error;

                this.currentProduct = {
                    ...data,
                    farmer_name: data.farmer?.username,
                    farmer_phone: data.farmer?.phone,
                    farmer_location: data.farmer?.location
                };
            } catch (error) {
                this.error = error.message || 'Failed to fetch product';
            } finally {
                this.isLoading = false;
            }
        },

        async fetchMyProducts(farmerId) {
            this.isLoading = true;
            this.error = null;
            try {
                const { data, error } = await supabase
                    .from('products')
                    .select('*')
                    .eq('farmer_id', farmerId)
                    .order('created_at', { ascending: false });

                if (error) throw error;
                return data;
            } catch (error) {
                this.error = error.message || 'Failed to fetch your products';
                return [];
            } finally {
                this.isLoading = false;
            }
        },

        async createProduct(productData) {
            this.isLoading = true;
            this.error = null;
            try {
                // Get current user for farmer_id
                const { data: { user } } = await supabase.auth.getUser();

                if (!user) throw new Error('User not authenticated');

                const productWithFarmer = {
                    ...productData,
                    farmer_id: user.id
                };

                console.log('DEBUG: Creating product');
                console.log('DEBUG: User ID:', user.id);
                console.log('DEBUG: Payload:', productWithFarmer);

                const { data, error } = await supabase
                    .from('products')
                    .insert(productWithFarmer)
                    .select()
                    .single();

                if (error) throw error;

                this.products.unshift(data);
                return data;
            } catch (error) {
                this.error = error.message || 'Failed to create product';
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        async updateProduct(id, productData) {
            this.isLoading = true;
            this.error = null;
            try {
                const { data, error } = await supabase
                    .from('products')
                    .update(productData)
                    .eq('id', id)
                    .select()
                    .single();

                if (error) throw error;

                const index = this.products.findIndex(p => p.id === id);
                if (index !== -1) {
                    this.products[index] = data;
                }
                if (this.currentProduct && this.currentProduct.id === id) {
                    this.currentProduct = data;
                }
                return data;
            } catch (error) {
                this.error = error.message || 'Failed to update product';
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        async deleteProduct(id) {
            this.isLoading = true;
            try {
                const { error } = await supabase
                    .from('products')
                    .delete()
                    .eq('id', id);

                if (error) throw error;

                this.products = this.products.filter(p => p.id !== id);
            } catch (error) {
                this.error = error.message || 'Failed to delete product';
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        setFilters(filters) {
            this.filters = { ...this.filters, ...filters };
        },

        clearFilters() {
            this.filters = { category: '' };
        }
    }
});
