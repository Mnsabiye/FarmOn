// Supabase client configuration
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Validate environment variables
if (!supabaseUrl || !supabaseAnonKey) {
    console.error('Missing Supabase environment variables!');
    console.error('Please create a .env.local file in the frontend directory with:');
    console.error('VITE_SUPABASE_URL=your-supabase-url');
    console.error('VITE_SUPABASE_ANON_KEY=your-anon-key');

    // Throw a more helpful error
    throw new Error(
        'Supabase configuration missing. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env.local file.'
    );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
