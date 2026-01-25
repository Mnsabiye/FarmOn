// Supabase Storage service for file uploads
import { supabase } from '../supabase';

export const storageService = {
    /**
     * Upload a product image to Supabase Storage
     * @param {File} file - The image file to upload
     * @param {string} productId - The product ID for organizing files
     * @returns {string} - The public URL of the uploaded image
     */
    async uploadProductImage(file, productId) {
        const fileExt = file.name.split('.').pop();
        const fileName = `${productId}-${Date.now()}.${fileExt}`;
        const filePath = `products/${fileName}`;

        const { error } = await supabase.storage
            .from('product-images')
            .upload(filePath, file);

        if (error) throw error;

        const { data } = supabase.storage
            .from('product-images')
            .getPublicUrl(filePath);

        return data.publicUrl;
    },

    /**
     * Upload a user avatar to Supabase Storage
     * @param {File} file - The avatar image file
     * @param {string} userId - The user ID
     * @returns {string} - The public URL of the uploaded avatar
     */
    async uploadUserAvatar(file, userId) {
        const fileExt = file.name.split('.').pop();
        const fileName = `${userId}-${Date.now()}.${fileExt}`;
        const filePath = `avatars/${fileName}`;

        const { error } = await supabase.storage
            .from('avatars')
            .upload(filePath, file);

        if (error) throw error;

        const { data } = supabase.storage
            .from('avatars')
            .getPublicUrl(filePath);

        return data.publicUrl;
    },

    /**
     * Delete a file from storage
     * @param {string} bucket - The storage bucket name
     * @param {string} filePath - The file path within the bucket
     */
    async deleteFile(bucket, filePath) {
        const { error } = await supabase.storage
            .from(bucket)
            .remove([filePath]);

        if (error) throw error;
    }
};
