import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

response = supabase.table("annonces").select("id").execute()

total = len(response.data)

print(f"Nombre total d'annonces : {total}")

if total >= 300:
    print("OK : objectif atteint, au moins 300 annonces.")
else:
    print(f"PAS ASSEZ : il manque {300 - total} annonces. Il faut scraper.")
