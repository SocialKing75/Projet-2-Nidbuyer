"""
Scrape BienIci annonces et les exporte en CSV.

Usage:
    python scraper_to_csv.py [--size 100] [--output annonces.csv]
"""
import csv
import json
import sys
from argparse import ArgumentParser
import requests


def get_bienici_ads(city: str = "Toulon", operation_type: str = "SALE", size: int = 100, offset: int = 0) -> list[dict]:
    """Récupère les annonces de l'API BienIci."""
    api_url = "https://www.bienici.com/realEstateAds.json"
    filters = {"operationType": [operation_type], "city": [city]}
    params = {
        "filters": json.dumps(filters, ensure_ascii=False),
        "size": str(size),
        "from": str(offset),
    }
    headers = {"User-Agent": "Mozilla/5.0"}

    print(f"Requête BienIci ({size} annonces)...")
    response = requests.get(api_url, params=params, headers=headers, timeout=15)
    response.raise_for_status()

    payload = response.json()
    ads = payload.get("realEstateAds", [])
    print(f"  → {len(ads)} annonce(s) trouvée(s)")
    return ads


def normalize_bienici_ad(raw: dict) -> dict:
    """Normalise une annonce BienIci vers le format standard."""
    return {
        "id_source": str(raw.get("id", "")),
        "url_source": f"https://www.bienici.com/annonce/{raw.get('id', '')}",
        "type": raw.get("propertyType", ""),
        "surface": raw.get("surfaceArea"),
        "prix": raw.get("price"),
        "quartier": raw.get("district", {}).get("name", ""),
        "ville": raw.get("city", "Toulon"),
        "description": raw.get("description", "")[:200],  # Limiter la description
        "photos_count": len(raw.get("photos", [])),
        "nb_pieces": raw.get("roomsQuantity"),
        "dpe": raw.get("energyClassification", ""),
    }


def export_to_csv(annonces: list[dict], output_file: str) -> None:
    """Exporte les annonces en CSV."""
    if not annonces:
        print("Aucune annonce à exporter.")
        return

    fieldnames = list(annonces[0].keys())
    
    print(f"Écriture dans {output_file}...")
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(annonces)
    
    print(f"✓ {len(annonces)} annonce(s) exportée(s) dans {output_file}")


if __name__ == "__main__":
    parser = ArgumentParser(description="Scrape BienIci → CSV")
    parser.add_argument("--size", type=int, default=100, help="Nombre d'annonces (défaut 100)")
    parser.add_argument("--output", type=str, default="annonces.csv", help="Fichier de sortie (défaut annonces.csv)")
    args = parser.parse_args()

    try:
        raw_annonces = get_bienici_ads(city="Toulon", operation_type="SALE", size=args.size)
        annonces = [normalize_bienici_ad(raw) for raw in raw_annonces]
        export_to_csv(annonces, args.output)
        print("\nExport réussi !")
    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        sys.exit(1)
