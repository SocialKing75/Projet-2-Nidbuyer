"""
Source : Bien'ici — annonces immobilières à Toulon.

Bien'ici expose une API JSON non-officielle utilisée par leur site web
(visible dans les DevTools). Le zoneId de Toulon vient de leur autocomplétion :
https://res.bienici.com/suggest.json?q=toulon
"""
import json
import logging
import time

import requests

from .base import SourceBase

logger = logging.getLogger(__name__)


class BienIciSource(SourceBase):
    name = "bienici"

    API_URL = "https://www.bienici.com/realEstateAds.json"
    ZONE_TOULON = "-35280"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    PAGE_SIZE = 100

    def fetch_new(self, target_size: int = 300) -> list[dict]:
        """Récupère jusqu'à target_size annonces à vendre (flat/house) sur Toulon."""
        annonces: list[dict] = []
        for offset in range(0, target_size, self.PAGE_SIZE):
            filters = {
                "size": min(self.PAGE_SIZE, target_size - offset),
                "from": offset,
                "filterType": "buy",
                "propertyType": ["flat", "house"],
                "page": offset // self.PAGE_SIZE + 1,
                "sortBy": "relevance",
                "sortOrder": "desc",
                "onTheMarket": [True],
                "zoneIdsByTypes": {"zoneIds": [self.ZONE_TOULON]},
            }
            response = requests.get(
                self.API_URL,
                params={"filters": json.dumps(filters)},
                headers=self.HEADERS,
                timeout=30,
            )
            response.raise_for_status()
            ads = response.json().get("realEstateAds", [])
            if not ads:
                break
            annonces.extend(self.normalize(self._parse(a)) for a in ads)
            time.sleep(1)  # ponytail: politesse anti-ban, 1 req/s suffit pour 300 annonces

        propres = [
            a for a in annonces
            if (a.get("prix") or 0) > 10_000 and 9 <= (a.get("surface") or 0) < 1_000
        ]
        logger.info("bienici : %s annonces récupérées, %s après filtre qualité",
                    len(annonces), len(propres))
        return propres

    def _parse(self, raw: dict) -> dict:
        """Convertit un objet annonce BienIci vers le format standard."""
        pieces = raw.get("roomsQuantity")
        base_type = {"flat": "Appartement", "house": "Maison"}.get(
            raw.get("propertyType"), raw.get("propertyType") or "")
        type_bien = f"{base_type} T{pieces}" if pieces else base_type
        quartier = (raw.get("district") or {}).get("name", "") or ""
        return {
            "id_source":   str(raw.get("id", "")),
            "url_source":  f"https://www.bienici.com/annonce/{raw.get('id', '')}",
            "type":        type_bien,
            "surface":     raw.get("surfaceArea"),
            "prix":        raw.get("price"),
            "quartier":    quartier.replace("Toulon - ", ""),
            "ville":       raw.get("city", "Toulon"),
            "description": raw.get("description", ""),
            "photos":      [p.get("url", "") for p in raw.get("photos", [])],
            "nb_pieces":   pieces,
            "dpe":         raw.get("energyClassification"),
        }
