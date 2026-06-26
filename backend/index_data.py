"""Indexe dans ChromaDB les annonces stockees dans Supabase."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.rag import get_collection, indexer_annonces  # noqa: E402


def get_annonces() -> list[dict]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL et SUPABASE_KEY doivent etre definis.")

    supabase = create_client(url, key)
    response = supabase.table("annonces").select("*").execute()
    return response.data or []


def main() -> None:
    load_dotenv()
    annonces = get_annonces()
    print(f"{len(annonces)} annonces recuperees depuis Supabase")

    indexer_annonces(annonces)

    count = get_collection().count()
    print(f"{count} annonces indexees dans ChromaDB")


if __name__ == "__main__":
    main()
