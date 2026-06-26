"""
Importe data/annonces_p1.csv dans Supabase avec deduplication url_source.

Usage:
    python -m backend.sources.import_p1_to_supabase --test-connection
    python -m backend.sources.import_p1_to_supabase --dry-run --limit 5
    python -m backend.sources.import_p1_to_supabase --limit 20
"""
from __future__ import annotations

import csv
import json
import os
import re
from argparse import ArgumentParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


CSV_PATH = Path("data/annonces_p1.csv")
SUPABASE_COLUMNS = [
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


def load_environment() -> None:
    """Charge .env puis .env.example en fallback local."""
    if load_dotenv:
        load_dotenv()
    else:
        _load_env_file(Path(".env"))
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        if load_dotenv:
            load_dotenv(".env.example")
        else:
            _load_env_file(Path(".env.example"))


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_supabase_config() -> tuple[str, str]:
    load_environment()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL et SUPABASE_KEY doivent etre definis dans .env")
    return url.rstrip("/").removesuffix("/rest/v1"), key


def _to_number(value):
    if value in ("", None):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return value
    return int(number) if number.is_integer() else number


def _clean_row(row: dict) -> dict:
    cleaned = {}
    for column in SUPABASE_COLUMNS:
        value = row.get(column)
        if column in {"surface", "prix", "nb_pieces", "photos_count"}:
            value = _to_number(value)
        if value not in ("", None):
            cleaned[column] = value
    return cleaned


def load_csv(path: Path = CSV_PATH) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"CSV introuvable : {path}")

    annonces = []
    seen_urls = set()
    with path.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            normalized = {str(k).lower().strip(): v for k, v in row.items()}
            annonce = _clean_row(normalized)
            url = annonce.get("url_source")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            annonces.append(annonce)
    return annonces


def supabase_request(method: str, path: str, payload: list[dict] | dict | None = None):
    base_url, key = get_supabase_config()
    url = f"{base_url}/rest/v1/{path.lstrip('/')}"
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if method.upper() == "POST":
        headers["Prefer"] = "resolution=merge-duplicates,return=minimal"

    request = Request(url, data=body, headers=headers, method=method.upper())
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else None
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore")
        raise RuntimeError(f"Erreur Supabase {exc.code}: {detail}") from exc


def _remove_column(rows: list[dict], column: str) -> list[dict]:
    return [{k: v for k, v in row.items() if k != column} for row in rows]


def _upsert_batch_adaptive(batch: list[dict]) -> None:
    """Upsert en retirant les colonnes absentes du schema Supabase."""
    query = urlencode({"on_conflict": "url_source"})
    current_batch = batch
    removed_columns: list[str] = []

    while current_batch and current_batch[0]:
        try:
            supabase_request("POST", f"annonces?{query}", current_batch)
            if removed_columns:
                print(f"Colonnes ignorees par Supabase : {', '.join(removed_columns)}")
            return
        except RuntimeError as exc:
            message = str(exc)
            match = re.search(r"Could not find the '([^']+)' column", message)
            if not match:
                raise
            missing_column = match.group(1)
            removed_columns.append(missing_column)
            current_batch = _remove_column(current_batch, missing_column)

    raise RuntimeError("Aucune colonne compatible avec la table Supabase annonces.")


def test_connection() -> bool:
    status, _ = supabase_request("GET", "annonces?select=url_source&limit=1")
    return 200 <= status < 300


def import_csv_to_supabase(path: Path = CSV_PATH, dry_run: bool = False, limit: int | None = None) -> int:
    annonces = load_csv(path)
    if limit is not None:
        annonces = annonces[:limit]
    return import_annonces_to_supabase(annonces, dry_run=dry_run)


def import_annonces_to_supabase(annonces: list[dict], dry_run: bool = False) -> int:
    seen_urls = set()
    annonces_uniques = []
    for annonce in annonces:
        url = annonce.get("url_source")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        annonces_uniques.append(annonce)
    annonces = annonces_uniques

    if dry_run:
        print(f"DRY RUN : {len(annonces)} annonce(s) prete(s) pour Supabase")
        return len(annonces)

    batch_size = 100
    for start in range(0, len(annonces), batch_size):
        batch = annonces[start:start + batch_size]
        _upsert_batch_adaptive(batch)
        print(f"Import Supabase : {min(start + batch_size, len(annonces))}/{len(annonces)}")
    return len(annonces)


def main() -> None:
    parser = ArgumentParser(description="Import CSV annonces P1 vers Supabase")
    parser.add_argument("--csv", type=Path, default=CSV_PATH)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--test-connection", action="store_true")
    args = parser.parse_args()

    if args.test_connection:
        ok = test_connection()
        print("Connexion Supabase OK" if ok else "Connexion Supabase KO")
        return

    count = import_csv_to_supabase(args.csv, dry_run=args.dry_run, limit=args.limit)
    print(f"{count} annonce(s) traitee(s) avec dedup url_source")


if __name__ == "__main__":
    main()
