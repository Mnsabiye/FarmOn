-- FarmConnect Database Schema for Supabase
-- Run this SQL in the Supabase SQL Editor to create all required tables

-- ============================================
-- USERS TABLE
-- Extends Supabase auth.users with profile info
-- ============================================
CREATE TABLE IF NOT EXISTS public.users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username VARCHAR(80) UNIQUE NOT NULL,
  email VARCHAR(120) UNIQUE NOT NULL,
  role VARCHAR(20) NOT NULL CHECK (role IN ('farmer', 'buyer', 'admin')),
  phone VARCHAR(20),
  location VARCHAR(100),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- PRODUCTS TABLE
-- Marketplace product listings
-- ============================================
CREATE TABLE IF NOT EXISTS public.products (
  id SERIAL PRIMARY KEY,
  farmer_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  category VARCHAR(50) NOT NULL,
  price_per_kg DECIMAL(10,2) NOT NULL,
  quantity_available DECIMAL(10,2) NOT NULL,
  description TEXT,
  image_url VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- MARKET PRICES TABLE
-- Track crop prices at different markets
-- ============================================
CREATE TABLE IF NOT EXISTS public.market_prices (
  id SERIAL PRIMARY KEY,
  crop_name VARCHAR(100) NOT NULL,
  market_location VARCHAR(100) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  date_recorded TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- CHAT MESSAGES TABLE
-- Store chatbot conversation history
-- ============================================
CREATE TABLE IF NOT EXISTS public.chat_messages (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES public.users(id),
  message_text TEXT NOT NULL,
  sender VARCHAR(10) NOT NULL CHECK (sender IN ('user', 'bot')),
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS POLICIES FOR USERS
-- ============================================
-- Anyone can view user profiles (for product listings)
CREATE POLICY "Users can view all profiles" ON public.users
  FOR SELECT USING (true);

-- Users can only insert their own profile (during registration)
CREATE POLICY "Users can insert own profile" ON public.users
  FOR INSERT WITH CHECK (auth.uid() = id);

-- Users can only update their own profile
CREATE POLICY "Users can update own profile" ON public.users
  FOR UPDATE USING (auth.uid() = id);

-- ============================================
-- RLS POLICIES FOR PRODUCTS
-- ============================================
-- Anyone can view products (public marketplace)
CREATE POLICY "Anyone can view products" ON public.products
  FOR SELECT USING (true);

-- Only farmers can create products (using their own ID)
CREATE POLICY "Farmers can insert own products" ON public.products
  FOR INSERT WITH CHECK (auth.uid() = farmer_id);

-- Farmers can only update their own products
CREATE POLICY "Farmers can update own products" ON public.products
  FOR UPDATE USING (auth.uid() = farmer_id);

-- Farmers can only delete their own products
CREATE POLICY "Farmers can delete own products" ON public.products
  FOR DELETE USING (auth.uid() = farmer_id);

-- ============================================
-- RLS POLICIES FOR MARKET PRICES
-- ============================================
-- Anyone can view market prices
CREATE POLICY "Anyone can view market prices" ON public.market_prices
  FOR SELECT USING (true);

-- Only admins can insert/update market prices (via service role key)
-- The service role key bypasses RLS, so no INSERT/UPDATE policy needed for regular users

-- ============================================
-- RLS POLICIES FOR CHAT MESSAGES
-- ============================================
-- Users can view their own messages or anonymous messages
CREATE POLICY "Users can view own messages" ON public.chat_messages
  FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

-- Users can insert their own messages or anonymous messages
CREATE POLICY "Users can insert messages" ON public.chat_messages
  FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- ============================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX IF NOT EXISTS idx_products_farmer_id ON public.products(farmer_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON public.products(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_market_prices_crop ON public.market_prices(crop_name);
CREATE INDEX IF NOT EXISTS idx_market_prices_date ON public.market_prices(date_recorded DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user ON public.chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON public.chat_messages(timestamp DESC);

-- ============================================
-- SEED DATA: Sample Market Prices
-- ============================================
INSERT INTO public.market_prices (crop_name, market_location, price) VALUES
  ('Haricots', 'Bujumbura Central', 1800.00),
  ('Maïs', 'Bujumbura Central', 1200.00),
  ('Tomates', 'Bujumbura Central', 800.00),
  ('Pommes de terre', 'Gitega', 600.00),
  ('Riz', 'Bujumbura Central', 2200.00),
  ('Bananes', 'Ngozi', 400.00),
  ('Manioc', 'Gitega', 300.00),
  ('Oignons', 'Bujumbura Central', 1500.00);
