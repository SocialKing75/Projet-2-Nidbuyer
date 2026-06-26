"""
Import P1 : importe les annonces BienIci dans Supabase et indexe ChromaDB.

Usage:
    python backend/import_p1_to_supabase.py [--dry-run] [--size 100]
"""
import json
import logging
import sys
import os
from argparse import ArgumentParser

import requests
from dotenv import load_dotenv

# Conditional import de supabase pour éviter les erreurs si non disponible
try:
    from supabase import create_client
except ImportError:
    create_client = None

from .ingestion import sync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.getenv("https://gpphjhrjsfhitkvrenuj.supabase.co")
SUPABASE_KEY = os.getenv("sb_publishable_ct7LNygRYsxriAr86pxC4A_6jHiASHI")


def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL et SUPABASE_KEY doivent être définis dans .env"
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)


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

    logger.info(f"Requête BienIci : {api_url} - {len(params)} param(s)")
    response = requests.get(api_url, params=params, headers=headers, timeout=15)
    response.raise_for_status()

    payload = response.json()
    ads = payload.get("realEstateAds", [])
    logger.info(f"BienIci a retourné {len(ads)} annonce(s)")
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
        "description": raw.get("description", ""),
        "photos": [photo.get("url", "") for photo in raw.get("photos", [])],
        "nb_pieces": raw.get("roomsQuantity"),
        "dpe": raw.get("energyClassification"),
        "source": "bienici",
    }


def import_annonces_to_supabase(annonces: list[dict], dry_run: bool = False) -> int:
    """
    Importe les annonces normalisées dans Supabase.

    Args:
        annonces: liste d'annonces normalisées
        dry_run: si True, affiche sans insérer

    Returns:
        Nombre d'annonces importées
    """
    if not annonces:
        logger.warning("Aucune annonce à importer.")
        return 0

    logger.info(f"Préparation de {len(annonces)} annonce(s) pour Supabase...")

    if dry_run:
        logger.info(f"DRY RUN : {len(annonces)} annonce(s) auraient été importées")
        for ann in annonces[:3]:
            logger.debug(f"  Aperçu : {ann.get('url_source')} - {ann.get('prix')}€")
        return len(annonces)

    supabase = get_supabase_client()
    count = 0

    for annonce in annonces:
        try:
            supabase.table("annonces").upsert(
                annonce,
                on_conflict="url_source"
            ).execute()
            count += 1
            if count % 10 == 0:
                logger.info(f"  {count}/{len(annonces)} annonce(s) importées...")
        except Exception as e:
            logger.error(f"Erreur lors de l'import {annonce.get('url_source')}: {e}")

    logger.info(f"{count}/{len(annonces)} annonce(s) importées avec succès dans Supabase")
    return count


def main(dry_run: bool = False, size: int = 100) -> None:
    """Lance le pipeline d'import P1."""
    logger.info("=== Démarrage de l'import P1 ===")
    logger.info(f"Paramètres : dry_run={dry_run}, size={size}")

    try:
        # 1. Récupérer les annonces BienIci
        logger.info("Étape 1 : Récupération des annonces BienIci...")
        raw_annonces = get_bienici_ads(city="Toulon", operation_type="SALE", size=size)
        logger.info(f"  → {len(raw_annonces)} annonce(s) trouvées")

        # 2. Normaliser
        logger.info("Étape 2 : Normalisation...")
        annonces = [normalize_bienici_ad(raw) for raw in raw_annonces]
        logger.info(f"  → {len(annonces)} annonce(s) normalisées")

        # 3. Importer dans Supabase
        logger.info("Étape 3 : Import Supabase...")
        imported = import_annonces_to_supabase(annonces, dry_run=dry_run)
        logger.info(f"  → {imported} annonce(s) importées")

        if dry_run:
            logger.info("=== DRY RUN : Import Supabase non effectué ===")
            return

        # 4. Indexer dans ChromaDB
        logger.info("Étape 4 : Indexation ChromaDB...")
        rapport = sync(dry_run=False)
        logger.info(f"  → Sync report : {rapport}")

        logger.info("=== Import P1 terminé avec succès ===")

    except Exception as e:
        logger.error(f"Erreur critique : {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    parser = ArgumentParser(description="Import P1 : BienIci → Supabase → ChromaDB")
    parser.add_argument("--dry-run", action="store_true", help="Simulation sans insérer")
    parser.add_argument("--size", type=int, default=100, help="Nombre d'annonces à importer (par défaut 100)")
    args = parser.parse_args()

    main(dry_run=args.dry_run, size=args.size)
