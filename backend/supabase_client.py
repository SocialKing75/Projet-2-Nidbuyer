import os
from supabase import create_client
from dotenv import load_dotenv

# Charger les variables .env
load_dotenv()

# Récupérer les infos Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# Créer le client Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
