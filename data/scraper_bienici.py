import json
import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


def save_annonce(annonce: dict) -> None:
    if not supabase:
        raise RuntimeError("SUPABASE_URL ou SUPABASE_KEY non définie(s).")

    supabase.table("annonces").upsert(
        annonce,
        on_conflict="url_source"
    ).execute()


def get_bienici_ads(city: str = "Toulon", operation_type: str = "SALE", size: int = 60, offset: int = 0) -> list[dict]:
    api_url = "https://www.bienici.com/realEstateAds.json"
    filters = {"operationType": [operation_type], "city": [city]}
    params = {
        "filters": json.dumps(filters, ensure_ascii=False),
        "size": str(size),
        "from": str(offset),
    }
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(api_url, params=params, headers=headers, timeout=15)
    response.raise_for_status()

    payload = response.json()
    return payload.get("realEstateAds", [])


def normalize_bienici_ad(raw: dict) -> dict:
    return {
        "id_source": str(raw.get("id", "")),
        "url_source": f"https://www.bienici.com/annonce/{raw.get('id', '')}",
        "type": raw.get("propertyType", ""),
        "surface": raw.get("surfaceArea"),
        "prix": raw.get("price"),
        "quartier": raw.get("district", {}).get("name", ""),
        "ville": raw.get("city", "Toulon"),
        "description": raw.get("description", ""),
        "photos": [photo.get("url", "") for photo in raw.get("photos", [])],
        "nb_pieces": raw.get("roomsQuantity"),
        "dpe": raw.get("energyClassification"),
    }


def scraper_bienici_toulon() -> list[dict]:
    raw_annonces = get_bienici_ads(city="Toulon", operation_type="SALE", size=60, offset=0)
    return [normalize_bienici_ad(raw) for raw in raw_annonces]


if __name__ == "__main__":
    annonces = scraper_bienici_toulon()

    print(f"{len(annonces)} annonces trouvées.")

    if supabase:
        for annonce in annonces:
            save_annonce(annonce)

        print(f"{len(annonces)} annonces envoyées dans Supabase")
        response = supabase.table("annonces").select("id").execute()
        print(len(response.data))
    else:
        print("SUPABASE_URL ou SUPABASE_KEY non définies. Les annonces ne sont pas envoyées dans Supabase.")