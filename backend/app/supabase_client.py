"""
Supabase client configuration for Flask backend.
"""
import os
from supabase import create_client, Client

# Get Supabase credentials from environment
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Initialize Supabase client
supabase: Client = create_client(url, key) if url and key else None


def get_supabase() -> Client:
    """Get the Supabase client instance."""
    if supabase is None:
        raise ValueError("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables.")
    return supabase


def verify_token(token: str) -> dict:
    """
    Verify a Supabase JWT token and return the user data.
    
    Args:
        token: The JWT token from the Authorization header
        
    Returns:
        dict: The user data from the token
        
    Raises:
        Exception: If token verification fails
    """
    try:
        # Get user from Supabase Auth
        user = supabase.auth.get_user(token)
        return user.user
    except Exception as e:
        raise ValueError(f"Invalid token: {str(e)}")
