"""Tests for the RAG module."""

import pytest
from backend import rag

@pytest.fixture(autouse=True)
def reset_chromadb():
    """Reset the in-memory ChromaDB collection before each test."""
    try:
        rag.client.delete_collection("annonces")
    except Exception:
        pass
    rag.get_collection()

def test_indexation_et_recherche():
    """Test indexing a property and searching for it."""
    annonce = {
        "id": "1",
        "type": "T3",
        "surface": 68,
        "quartier": "Mourillon",
        "description": "Vue mer calme"
    }
    rag.index_annonces([annonce])
    
    results = rag.search_similar("T3 calme proche mer", n=5)
    assert len(results) > 0
    assert results[0]["quartier"] == "Mourillon"

def test_recherche_retourne_n_resultats():
    """Test that search returns exactly n results."""
    annonces = [
        {"id": "1", "type": "T3", "surface": 68, "quartier": "Mourillon", "description": "Vue mer calme"},
        {"id": "2", "type": "T2", "surface": 45, "quartier": "Port", "description": "Beau T2 rénové"},
        {"id": "3", "type": "T4", "surface": 90, "quartier": "Cap Brun", "description": "Villa avec piscine"}
    ]
    rag.index_annonces(annonces)
    
    results = rag.search_similar("appartement", n=2)
    assert len(results) == 2
