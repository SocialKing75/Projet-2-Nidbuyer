"""Indexation et recherche sémantique — ChromaDB."""
import os

import chromadb
from chromadb.utils import embedding_functions

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_real_client = None
_ef = None


def _get_real_client():
    global _real_client
    if _real_client is None:
        path = os.environ.get("CHROMA_PATH")
        if path:
            _real_client = chromadb.PersistentClient(path=path)
        else:
            _real_client = chromadb.EphemeralClient()
    return _real_client


def _get_ef():
    global _ef
    if _ef is None:
        _ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    return _ef


class _LazyClient:
    """Proxy vers le vrai client ChromaDB — initialisé à la première utilisation."""
    def __getattr__(self, name):
        return getattr(_get_real_client(), name)


# Exposé pour les tests : rag.client.delete_collection(...)
client = _LazyClient()


def get_collection():
    return _get_real_client().get_or_create_collection(
        name="annonces",
        embedding_function=_get_ef(),
    )


def _sanitize(d: dict) -> dict:
    result = {}
    for k, v in d.items():
        if v is None:
            result[k] = ""
        elif isinstance(v, (str, int, float, bool)):
            result[k] = v
        elif isinstance(v, list):
            result[k] = ", ".join(str(x) for x in v)
        else:
            result[k] = str(v)
    return result


def index_annonces(annonces: list[dict]) -> None:
    """Indexe une liste d'annonces dans ChromaDB."""
    collection = get_collection()
    ids, documents, metadatas = [], [], []
    for i, a in enumerate(annonces):
        # id absent selon la source (ex. Supabase) : repli sur id_source/url_source/rang
        ids.append(str(a.get("id") or a.get("id_source") or a.get("url_source") or i))
        documents.append(a.get("description", "") or "")
        meta = _sanitize({k: v for k, v in a.items() if k != "description"})
        metadatas.append(meta or {"id": ids[-1]})  # Chroma refuse les metadata vides
    if ids:
        # upsert : ré-indexation idempotente (add lève DuplicateIDError)
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)


# Alias pour l'ingestion
indexer_annonces = index_annonces


def search_similar(query: str, n: int = 5, filtre_meta: dict | None = None) -> list[dict]:
    """Recherche sémantique — retourne les n biens les plus proches."""
    try:
        collection = get_collection()
        results = collection.query(
            query_texts=[query],
            n_results=n,
            where=filtre_meta if filtre_meta else None,
        )
        biens = []
        if results and results["metadatas"]:
            for i, meta in enumerate(results["metadatas"][0]):
                bien = meta.copy()
                bien["similarity"] = results["distances"][0][i] if results.get("distances") else 0
                biens.append(bien)
        return biens
    except Exception:
        return []
