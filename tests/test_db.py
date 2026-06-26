"""Test de connexion à la base de données Supabase.
Ce test est ignoré en CI (pas de vraies credentials) — il sert à valider
manuellement la connexion depuis un environnement avec .env configuré.
"""
import pytest


@pytest.mark.skip(reason="Nécessite des credentials Supabase réels (.env)")
def test_supabase_connexion():
    from backend.supabase_client import supabase
    response = supabase.table("annonces").select("*").limit(3).execute()
    assert isinstance(response.data, list)
    print(f"{len(response.data)} annonces récupérées")
