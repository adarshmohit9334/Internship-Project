from supabase import create_client, Client
from config import Config

supabase: Client = None

def init_supabase(app):
    global supabase
    if Config.SUPABASE_URL and Config.SUPABASE_KEY:
        try:
            supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        except Exception as e:
            print(f"Failed to init Supabase: {e}")
            supabase = None
    else:
        print("Warning: Supabase credentials not found. App might not work fully without them or fallback mock DB.")
