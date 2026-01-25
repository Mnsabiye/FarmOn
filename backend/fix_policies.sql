-- FIX RLS POLICIES
-- Run this in Supabase SQL Editor

-- 1. Ensure Table Permissions
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;

-- 2. Drop existing policies to avoid conflicts
DROP POLICY IF EXISTS "Farmers can insert own products" ON public.products;
DROP POLICY IF EXISTS "Anyone can view products" ON public.products;
DROP POLICY IF EXISTS "Farmers can update own products" ON public.products;
DROP POLICY IF EXISTS "Farmers can delete own products" ON public.products;

-- 3. Re-create Policies
-- Allow anyone to view products
CREATE POLICY "Anyone can view products" ON public.products
  FOR SELECT USING (true);

-- Allow authenticated users to insert products (as long as they claim to be themselves)
CREATE POLICY "Farmers can insert own products" ON public.products
  FOR INSERT WITH CHECK (auth.uid() = farmer_id);

-- Allow farmers to edit their own products
CREATE POLICY "Farmers can update own products" ON public.products
  FOR UPDATE USING (auth.uid() = farmer_id);

-- Allow farmers to delete their own products
CREATE POLICY "Farmers can delete own products" ON public.products
  FOR DELETE USING (auth.uid() = farmer_id);
