"""
Genere le CSV P1 fusionne BienIci + LeBonCoin pour Toulon.

Le fichier produit respecte exactement ces colonnes :
id_source,url_source,type,surface,prix,quartier,ville,description,nb_pieces,photos_count,date_scraping
"""
from __future__ import annotations

import csv
import logging
from argparse import ArgumentParser
from pathlib import Path

from backend.sources.bienici import BienIciSource
from backend.sources.leboncoin import LeBonCoinBlocked, LeBonCoinSource


CSV_FIELDNAMES = [
    "id_source",
    "url_source",
    "type",
    "surface",
    "prix",
    "quartier",
    "ville",
    "description",
    "nb_pieces",
    "photos_count",
    "date_scraping",
]

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def to_csv_row(annonce: dict) -> dict:
    return {
        "id_source": annonce.get("id_source"),
        "url_source": annonce.get("url_source"),
        "type": annonce.get("type"),
        "surface": annonce.get("surface"),
        "prix": annonce.get("prix"),
        "quartier": annonce.get("quartier"),
        "ville": annonce.get("ville"),
        "description": (annonce.get("description") or "")[:500],
        "nb_pieces": annonce.get("nb_pieces"),
        "photos_count": annonce.get("photos_count", len(annonce.get("photos") or [])),
        "date_scraping": annonce.get("date_scraping"),
    }


def keep_toulon(annonce: dict) -> bool:
    return str(annonce.get("ville", "")).strip().casefold() == "toulon"


def dedupe_by_url_source(annonces: list[dict]) -> list[dict]:
    seen = set()
    uniques = []
    for annonce in annonces:
        url = annonce.get("url_source")
        if not url or url in seen:
            continue
        seen.add(url)
        uniques.append(annonce)
    return uniques


def fetch_all(bienici_size: int, leboncoin_size: int) -> tuple[list[dict], dict]:
    report = {"bienici": 0, "leboncoin": 0, "leboncoin_error": None}

    bienici = BienIciSource().fetch_new(target_size=bienici_size)
    report["bienici"] = len(bienici)

    try:
        leboncoin = LeBonCoinSource().fetch_new(target_size=leboncoin_size)
    except LeBonCoinBlocked as exc:
        logger.warning("%s", exc)
        leboncoin = []
        report["leboncoin_error"] = str(exc)
    report["leboncoin"] = len(leboncoin)

    annonces = [to_csv_row(a) for a in [*bienici, *leboncoin] if keep_toulon(a)]
    return dedupe_by_url_source(annonces), report


def write_csv(annonces: list[dict], output: Path) -> None:
    if not annonces:
        raise RuntimeError("Aucune annonce a ecrire.")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(annonces)


def main() -> None:
    parser = ArgumentParser(description="Fusion BienIci + LeBonCoin -> CSV Toulon")
    parser.add_argument("--output", type=Path, default=Path("data/annonces_p1.csv"))
    parser.add_argument("--bienici-size", type=int, default=300)
    parser.add_argument("--leboncoin-size", type=int, default=100)
    args = parser.parse_args()

    annonces, report = fetch_all(args.bienici_size, args.leboncoin_size)
    write_csv(annonces, args.output)
    logger.info("CSV genere : %s", args.output)
    logger.info("Sources : %s", report)
    logger.info("Total apres fusion/dedup url_source : %s", len(annonces))


if __name__ == "__main__":
    main()
