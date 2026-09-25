-- ADMIN DASHBOARD SETUP
-- Run this in the Supabase SQL Editor after supabase_schema.sql.
-- Safe to run more than once.

-- ============================================
-- 1. AUDIT LOG
-- Every action taken from the admin dashboard is recorded here.
-- Only the backend (service role key, which bypasses RLS) reads/writes it.
-- ============================================
CREATE TABLE IF NOT EXISTS public.admin_audit_log (
  id SERIAL PRIMARY KEY,
  admin_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
  action VARCHAR(50) NOT NULL,
  target_type VARCHAR(30) NOT NULL,
  target_id VARCHAR(64) NOT NULL,
  details JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.admin_audit_log ENABLE ROW LEVEL SECURITY;
-- No policies on purpose: regular (anon/authenticated) clients get no access.

CREATE INDEX IF NOT EXISTS idx_admin_audit_log_created_at ON public.admin_audit_log(created_at DESC);

-- ============================================
-- 2. PREVENT SELF-PROMOTION TO ADMIN
-- The existing policies let users insert and update their own profile row,
-- including the role column. Without this trigger anyone could register as
-- 'admin', or change their role to 'admin', and gain access to the admin
-- dashboard. Role changes are only allowed through the service role
-- (i.e. the admin API in the Flask backend).
-- ============================================
CREATE OR REPLACE FUNCTION public.protect_user_role()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  IF coalesce(auth.role(), '') = 'service_role' OR current_user IN ('postgres', 'supabase_admin') THEN
    RETURN NEW;
  END IF;

  IF TG_OP = 'INSERT' AND NEW.role = 'admin' THEN
    RAISE EXCEPTION 'Cannot register with the admin role';
  END IF;

  IF TG_OP = 'UPDATE' AND NEW.role IS DISTINCT FROM OLD.role THEN
    RAISE EXCEPTION 'Only an administrator can change a user role';
  END IF;

  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS protect_user_role ON public.users;
CREATE TRIGGER protect_user_role
  BEFORE INSERT OR UPDATE ON public.users
  FOR EACH ROW EXECUTE FUNCTION public.protect_user_role();

-- ============================================
-- 3. PROMOTE YOUR FIRST ADMIN
-- Register a normal account in the app, then run (with your email):
--
--   UPDATE public.users SET role = 'admin' WHERE email = 'you@example.com';
-- ============================================
